"""
API Gateway - Main Application

This is the central API Management layer that sits between external partners
and internal backend services. It provides:

1. Authentication - API key validation
2. Authorization - Service-level access control per partner
3. Rate Limiting - Per-partner request limits
4. Proxying - Forwards requests to backend services
5. Logging - Audit trail for all requests
"""

import time
from contextlib import asynccontextmanager

import httpx
from fastapi import Depends, FastAPI, HTTPException, Header, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

from partners import Partner, Service, partner_store
from rate_limiter import rate_limiter
from logging_service import request_logger


# Configuration
BASE_URL = "https://jsonplaceholder.typicode.com"

# Security scheme for Swagger UI
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Service path mapping
SERVICE_PATHS = {
    "users": Service.USERS,
    "posts": Service.POSTS,
    "comments": Service.COMMENTS,
    "todos": Service.TODOS,
    "albums": Service.ALBUMS,
    "photos": Service.PHOTOS,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    print("🚀 API Gateway starting up...")
    print(f"📡 Backend URL: {BASE_URL}")
    print(f"👥 Registered partners: {len(partner_store.list_partners())}")
    yield
    print("👋 API Gateway shutting down...")


app = FastAPI(
    title="API Gateway",
    description="API Management Layer for secure, controlled access to internal services",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Dependencies
# =============================================================================

async def get_partner(x_api_key: str = Depends(api_key_header)) -> Partner:
    """
    Validate API key and return the associated partner.
    
    Raises:
        HTTPException: 401 if API key is missing or invalid.
    """
    if x_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header is required",
            headers={"WWW-Authenticate": "API-Key"}
        )
    
    partner = partner_store.get_by_api_key(x_api_key)
    
    if partner is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "API-Key"}
        )
    
    if not partner.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Partner account is deactivated"
        )
    
    return partner


async def check_rate_limit(partner: Partner = Depends(get_partner)) -> Partner:
    """
    Check if the partner is within their rate limit.
    
    Raises:
        HTTPException: 429 if rate limit exceeded.
    """
    if not rate_limiter.is_allowed(partner.id, partner.rate_limit):
        remaining = rate_limiter.get_remaining(partner.id, partner.rate_limit)
        reset_time = rate_limiter.get_reset_time(partner.id)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Limit: {partner.rate_limit} requests/minute",
            headers={
                "X-RateLimit-Limit": str(partner.rate_limit),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(reset_time),
                "Retry-After": str(reset_time)
            }
        )
    return partner


def check_service_access(service: Service):
    """
    Factory to create a dependency that checks service access.
    """
    async def _check_access(partner: Partner = Depends(check_rate_limit)) -> Partner:
        if not partner.can_access(service):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied to {service.value} service. "
                       f"Allowed services: {[s.value for s in partner.allowed_services]}"
            )
        return partner
    return _check_access


# =============================================================================
# Proxy Function
# =============================================================================

async def proxy_to_backend(
    request: Request,
    backend_path: str,
    service: Service,
    partner: Partner,
    timeout: float = 30.0
) -> Response:
    """
    Forward request to backend service and log the result.
    """
    start_time = time.time()
    error_message = None
    status_code = 500
    
    try:
        # Build target URL
        target_url = f"{BASE_URL}/{backend_path}"
        if request.url.query:
            target_url = f"{target_url}?{request.url.query}"
        
        # Filter headers
        exclude_headers = {"host", "content-length", "transfer-encoding", "x-api-key"}
        forwarded_headers = {
            key: value
            for key, value in request.headers.items()
            if key.lower() not in exclude_headers
        }
        
        # Read request body
        body = await request.body()
        
        # Make the request
        async with httpx.AsyncClient(timeout=timeout) as client:
            backend_response = await client.request(
                method=request.method,
                url=target_url,
                headers=forwarded_headers,
                content=body if body else None,
            )
        
        status_code = backend_response.status_code
        content = backend_response.content
        
        # Add rate limit headers to response
        rate_limit_headers = {
            "X-RateLimit-Limit": str(partner.rate_limit),
            "X-RateLimit-Remaining": str(rate_limiter.get_remaining(partner.id, partner.rate_limit))
        }
        
        # Log the request on success
        response_time_ms = (time.time() - start_time) * 1000
        request_logger.log_request(
            partner_id=partner.id,
            partner_name=partner.name,
            method=request.method,
            path=backend_path,
            service=service.value,
            status_code=status_code,
            response_time_ms=response_time_ms,
            client_ip=request.client.host if request.client else None,
            error_message=None
        )
        
        return Response(
            content=content,
            status_code=status_code,
            headers=rate_limit_headers,
            media_type=backend_response.headers.get("content-type"),
        )
    
    except httpx.TimeoutException:
        error_message = "Backend service timeout"
        response_time_ms = (time.time() - start_time) * 1000
        request_logger.log_request(
            partner_id=partner.id,
            partner_name=partner.name,
            method=request.method,
            path=backend_path,
            service=service.value,
            status_code=504,
            response_time_ms=response_time_ms,
            client_ip=request.client.host if request.client else None,
            error_message=error_message
        )
        raise HTTPException(status_code=504, detail=error_message)
    
    except httpx.RequestError as e:
        error_message = f"Backend service error: {str(e)}"
        response_time_ms = (time.time() - start_time) * 1000
        request_logger.log_request(
            partner_id=partner.id,
            partner_name=partner.name,
            method=request.method,
            path=backend_path,
            service=service.value,
            status_code=502,
            response_time_ms=response_time_ms,
            client_ip=request.client.host if request.client else None,
            error_message=error_message
        )
        raise HTTPException(status_code=502, detail=error_message)


# =============================================================================
# Health & Info Endpoints (No Auth Required)
# =============================================================================

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "API Gateway"}


@app.get("/info", tags=["System"])
async def gateway_info():
    """Get information about the API Gateway."""
    return {
        "name": "API Gateway",
        "version": "1.0.0",
        "backend_url": BASE_URL,
        "available_services": [s.value for s in Service],
        "documentation": "/docs"
    }


# =============================================================================
# Partner Info Endpoint
# =============================================================================

@app.get("/me", tags=["Partner"])
async def get_my_info(partner: Partner = Depends(get_partner)):
    """Get information about the authenticated partner."""
    return {
        "id": partner.id,
        "name": partner.name,
        "allowed_services": [s.value for s in partner.allowed_services],
        "rate_limit": partner.rate_limit,
        "rate_limit_remaining": rate_limiter.get_remaining(partner.id, partner.rate_limit),
        "is_active": partner.is_active
    }


# =============================================================================
# Users Service Endpoints
# =============================================================================

@app.get("/api/users", tags=["Users Service"])
async def get_users(
    request: Request,
    partner: Partner = Depends(check_service_access(Service.USERS))
):
    """Get all users."""
    return await proxy_to_backend(request, "users", Service.USERS, partner)


@app.get("/api/users/{user_id}", tags=["Users Service"])
async def get_user(
    request: Request,
    user_id: int,
    partner: Partner = Depends(check_service_access(Service.USERS))
):
    """Get a specific user by ID."""
    return await proxy_to_backend(request, f"users/{user_id}", Service.USERS, partner)


@app.post("/api/users", tags=["Users Service"])
async def create_user(
    request: Request,
    partner: Partner = Depends(check_service_access(Service.USERS))
):
    """Create a new user."""
    return await proxy_to_backend(request, "users", Service.USERS, partner)


# =============================================================================
# Posts Service Endpoints
# =============================================================================

@app.get("/api/posts", tags=["Posts Service"])
async def get_posts(
    request: Request,
    partner: Partner = Depends(check_service_access(Service.POSTS))
):
    """Get all posts."""
    return await proxy_to_backend(request, "posts", Service.POSTS, partner)


@app.get("/api/posts/{post_id}", tags=["Posts Service"])
async def get_post(
    request: Request,
    post_id: int,
    partner: Partner = Depends(check_service_access(Service.POSTS))
):
    """Get a specific post by ID."""
    return await proxy_to_backend(request, f"posts/{post_id}", Service.POSTS, partner)


@app.post("/api/posts", tags=["Posts Service"])
async def create_post(
    request: Request,
    partner: Partner = Depends(check_service_access(Service.POSTS))
):
    """Create a new post."""
    return await proxy_to_backend(request, "posts", Service.POSTS, partner)


@app.put("/api/posts/{post_id}", tags=["Posts Service"])
async def update_post(
    request: Request,
    post_id: int,
    partner: Partner = Depends(check_service_access(Service.POSTS))
):
    """Update a post."""
    return await proxy_to_backend(request, f"posts/{post_id}", Service.POSTS, partner)


@app.delete("/api/posts/{post_id}", tags=["Posts Service"])
async def delete_post(
    request: Request,
    post_id: int,
    partner: Partner = Depends(check_service_access(Service.POSTS))
):
    """Delete a post."""
    return await proxy_to_backend(request, f"posts/{post_id}", Service.POSTS, partner)


@app.get("/api/posts/{post_id}/comments", tags=["Posts Service"])
async def get_post_comments(
    request: Request,
    post_id: int,
    partner: Partner = Depends(check_service_access(Service.COMMENTS))
):
    """Get comments for a specific post."""
    return await proxy_to_backend(request, f"posts/{post_id}/comments", Service.COMMENTS, partner)


# =============================================================================
# Comments Service Endpoints
# =============================================================================

@app.get("/api/comments", tags=["Comments Service"])
async def get_comments(
    request: Request,
    partner: Partner = Depends(check_service_access(Service.COMMENTS))
):
    """Get all comments."""
    return await proxy_to_backend(request, "comments", Service.COMMENTS, partner)


@app.get("/api/comments/{comment_id}", tags=["Comments Service"])
async def get_comment(
    request: Request,
    comment_id: int,
    partner: Partner = Depends(check_service_access(Service.COMMENTS))
):
    """Get a specific comment by ID."""
    return await proxy_to_backend(request, f"comments/{comment_id}", Service.COMMENTS, partner)


@app.post("/api/comments", tags=["Comments Service"])
async def create_comment(
    request: Request,
    partner: Partner = Depends(check_service_access(Service.COMMENTS))
):
    """Create a new comment."""
    return await proxy_to_backend(request, "comments", Service.COMMENTS, partner)


# =============================================================================
# Todos Service Endpoints
# =============================================================================

@app.get("/api/todos", tags=["Todos Service"])
async def get_todos(
    request: Request,
    partner: Partner = Depends(check_service_access(Service.TODOS))
):
    """Get all todos."""
    return await proxy_to_backend(request, "todos", Service.TODOS, partner)


@app.get("/api/todos/{todo_id}", tags=["Todos Service"])
async def get_todo(
    request: Request,
    todo_id: int,
    partner: Partner = Depends(check_service_access(Service.TODOS))
):
    """Get a specific todo by ID."""
    return await proxy_to_backend(request, f"todos/{todo_id}", Service.TODOS, partner)


@app.post("/api/todos", tags=["Todos Service"])
async def create_todo(
    request: Request,
    partner: Partner = Depends(check_service_access(Service.TODOS))
):
    """Create a new todo."""
    return await proxy_to_backend(request, "todos", Service.TODOS, partner)


# =============================================================================
# Albums Service Endpoints
# =============================================================================

@app.get("/api/albums", tags=["Albums Service"])
async def get_albums(
    request: Request,
    partner: Partner = Depends(check_service_access(Service.ALBUMS))
):
    """Get all albums."""
    return await proxy_to_backend(request, "albums", Service.ALBUMS, partner)


@app.get("/api/albums/{album_id}", tags=["Albums Service"])
async def get_album(
    request: Request,
    album_id: int,
    partner: Partner = Depends(check_service_access(Service.ALBUMS))
):
    """Get a specific album by ID."""
    return await proxy_to_backend(request, f"albums/{album_id}", Service.ALBUMS, partner)


@app.get("/api/albums/{album_id}/photos", tags=["Albums Service"])
async def get_album_photos(
    request: Request,
    album_id: int,
    partner: Partner = Depends(check_service_access(Service.PHOTOS))
):
    """Get photos in a specific album."""
    return await proxy_to_backend(request, f"albums/{album_id}/photos", Service.PHOTOS, partner)


# =============================================================================
# Photos Service Endpoints
# =============================================================================

@app.get("/api/photos", tags=["Photos Service"])
async def get_photos(
    request: Request,
    partner: Partner = Depends(check_service_access(Service.PHOTOS))
):
    """Get all photos."""
    return await proxy_to_backend(request, "photos", Service.PHOTOS, partner)


@app.get("/api/photos/{photo_id}", tags=["Photos Service"])
async def get_photo(
    request: Request,
    photo_id: int,
    partner: Partner = Depends(check_service_access(Service.PHOTOS))
):
    """Get a specific photo by ID."""
    return await proxy_to_backend(request, f"photos/{photo_id}", Service.PHOTOS, partner)


# =============================================================================
# Admin Endpoints (for monitoring)
# =============================================================================

@app.get("/admin/partners", tags=["Admin"])
async def list_partners(partner: Partner = Depends(get_partner)):
    """List all registered partners (admin only)."""
    # In production, add admin role check
    partners = partner_store.list_partners()
    return [
        {
            "id": p.id,
            "name": p.name,
            "allowed_services": [s.value for s in p.allowed_services],
            "rate_limit": p.rate_limit,
            "is_active": p.is_active
        }
        for p in partners
    ]


@app.get("/admin/logs", tags=["Admin"])
async def get_logs(
    limit: int = 100,
    partner: Partner = Depends(get_partner)
):
    """Get recent request logs (admin only)."""
    logs = request_logger.get_recent_logs(limit)
    return [
        {
            "id": log.id,
            "timestamp": log.timestamp,
            "partner": log.partner_name,
            "method": log.method,
            "path": log.path,
            "service": log.service,
            "status_code": log.status_code,
            "response_time_ms": round(log.response_time_ms, 2)
        }
        for log in logs
    ]


@app.get("/admin/stats", tags=["Admin"])
async def get_stats(partner: Partner = Depends(get_partner)):
    """Get aggregate statistics (admin only)."""
    return request_logger.get_stats()


# =============================================================================
# Run the application
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
