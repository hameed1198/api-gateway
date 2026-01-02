import httpx
from fastapi import Request, Response


async def proxy_request(
    request: Request,
    backend_url: str,
    timeout: float = 30.0,
    exclude_headers: set[str] | None = None,
) -> Response:
    """
    Async proxy function that forwards requests to a backend service.
    
    Args:
        request: The incoming FastAPI request.
        backend_url: The base URL of the backend service to forward to.
        timeout: Request timeout in seconds.
        exclude_headers: Headers to exclude from forwarding (e.g., {"host", "content-length"}).
        
    Returns:
        A FastAPI Response with the backend's response data.
    """
    if exclude_headers is None:
        exclude_headers = {"host", "content-length", "transfer-encoding"}
    
    # Build the target URL with query parameters
    target_url = backend_url
    if request.url.query:
        target_url = f"{backend_url}?{request.url.query}"
    
    # Filter and forward headers
    forwarded_headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in exclude_headers
    }
    
    # Read the request body
    body = await request.body()
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        # Forward the request with the same method
        backend_response = await client.request(
            method=request.method,
            url=target_url,
            headers=forwarded_headers,
            content=body if body else None,
        )
    
    # Filter response headers to exclude hop-by-hop headers
    response_headers = {
        key: value
        for key, value in backend_response.headers.items()
        if key.lower() not in {"transfer-encoding", "content-encoding", "connection"}
    }
    
    return Response(
        content=backend_response.content,
        status_code=backend_response.status_code,
        headers=response_headers,
        media_type=backend_response.headers.get("content-type"),
    )


async def proxy_request_streaming(
    request: Request,
    backend_url: str,
    timeout: float = 30.0,
    exclude_headers: set[str] | None = None,
):
    """
    Async proxy function with streaming support for large responses.
    
    Args:
        request: The incoming FastAPI request.
        backend_url: The base URL of the backend service to forward to.
        timeout: Request timeout in seconds.
        exclude_headers: Headers to exclude from forwarding.
        
    Yields:
        Chunks of the backend response for streaming.
    """
    from fastapi.responses import StreamingResponse
    
    if exclude_headers is None:
        exclude_headers = {"host", "content-length", "transfer-encoding"}
    
    # Build the target URL with query parameters
    target_url = backend_url
    if request.url.query:
        target_url = f"{backend_url}?{request.url.query}"
    
    # Filter and forward headers
    forwarded_headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in exclude_headers
    }
    
    # Read the request body
    body = await request.body()
    
    client = httpx.AsyncClient(timeout=timeout)
    
    async def stream_response():
        try:
            async with client.stream(
                method=request.method,
                url=target_url,
                headers=forwarded_headers,
                content=body if body else None,
            ) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk
        finally:
            await client.aclose()
    
    # Make initial request to get headers and status
    async with httpx.AsyncClient(timeout=timeout) as temp_client:
        response = await temp_client.request(
            method="HEAD" if request.method == "HEAD" else request.method,
            url=target_url,
            headers=forwarded_headers,
        )
        
        response_headers = {
            key: value
            for key, value in response.headers.items()
            if key.lower() not in {"transfer-encoding", "content-encoding", "connection", "content-length"}
        }
        
        return StreamingResponse(
            stream_response(),
            status_code=response.status_code,
            headers=response_headers,
            media_type=response.headers.get("content-type"),
        )
