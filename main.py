from fastapi import Depends, FastAPI, Request

from dependencies import check_rate_limit, verify_api_key
from proxy import proxy_request

app = FastAPI(title="EIGHTGEN AI API", version="1.0.0")

BASE_URL = "https://jsonplaceholder.typicode.com"


@app.get("/health")
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "healthy", "message": "API is running"}


@app.get("/protected")
async def protected_route(api_key: str = Depends(verify_api_key)):
    """Example protected endpoint that requires API key authentication."""
    return {"message": "Access granted", "api_key": api_key}


@app.api_route("/proxy/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_endpoint(request: Request, path: str):
    """
    Example proxy endpoint that forwards requests to a backend service.
    
    Usage: /proxy/api/users -> forwards to BASE_URL/api/users
    """
    backend_url = f"{BASE_URL}/{path}"
    return await proxy_request(request, backend_url)


# ============================================================================
# JSONPlaceholder API Routes (with API key auth + rate limiting)
# ============================================================================

@app.get("/api/posts")
async def get_posts(request: Request, api_key: str = Depends(check_rate_limit)):
    """Get all posts from JSONPlaceholder."""
    return await proxy_request(request, f"{BASE_URL}/posts")


@app.get("/api/posts/{post_id}")
async def get_post(request: Request, post_id: int, api_key: str = Depends(check_rate_limit)):
    """Get a specific post by ID."""
    return await proxy_request(request, f"{BASE_URL}/posts/{post_id}")


@app.post("/api/posts")
async def create_post(request: Request, api_key: str = Depends(check_rate_limit)):
    """Create a new post."""
    return await proxy_request(request, f"{BASE_URL}/posts")


@app.get("/api/users")
async def get_users(request: Request, api_key: str = Depends(check_rate_limit)):
    """Get all users from JSONPlaceholder."""
    return await proxy_request(request, f"{BASE_URL}/users")


@app.get("/api/users/{user_id}")
async def get_user(request: Request, user_id: int, api_key: str = Depends(check_rate_limit)):
    """Get a specific user by ID."""
    return await proxy_request(request, f"{BASE_URL}/users/{user_id}")


@app.get("/api/comments")
async def get_comments(request: Request, api_key: str = Depends(check_rate_limit)):
    """Get all comments from JSONPlaceholder."""
    return await proxy_request(request, f"{BASE_URL}/comments")


@app.post("/api/comments")
async def create_comment(request: Request, api_key: str = Depends(check_rate_limit)):
    """Create a new comment."""
    return await proxy_request(request, f"{BASE_URL}/comments")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
