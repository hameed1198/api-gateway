import time
from collections import defaultdict
from dataclasses import dataclass, field

from fastapi import Header, HTTPException, status

# Dictionary of valid API keys (in production, use a secure database or secrets manager)
API_KEYS = {
    "dev-key-123": "development",
    "prod-key-456": "production",
}


@dataclass
class RateLimitState:
    """Tracks request timestamps for rate limiting."""
    timestamps: list = field(default_factory=list)


class RateLimiter:
    """
    Simple in-memory rate limiter.
    
    Limits requests per API key with a configurable max requests per minute.
    """
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed per window.
            window_seconds: Time window in seconds (default: 60 for per-minute limiting).
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, RateLimitState] = defaultdict(RateLimitState)
    
    def is_allowed(self, api_key: str) -> bool:
        """
        Check if a request is allowed for the given API key.
        
        Args:
            api_key: The API key to check.
            
        Returns:
            True if the request is allowed, False if rate limit exceeded.
        """
        current_time = time.time()
        state = self._requests[api_key]
        
        # Remove timestamps outside the current window
        cutoff_time = current_time - self.window_seconds
        state.timestamps = [ts for ts in state.timestamps if ts > cutoff_time]
        
        # Check if under the limit
        if len(state.timestamps) >= self.max_requests:
            return False
        
        # Record this request
        state.timestamps.append(current_time)
        return True
    
    def get_remaining(self, api_key: str) -> int:
        """Get the number of remaining requests for an API key."""
        current_time = time.time()
        state = self._requests[api_key]
        cutoff_time = current_time - self.window_seconds
        valid_timestamps = [ts for ts in state.timestamps if ts > cutoff_time]
        return max(0, self.max_requests - len(valid_timestamps))


# Global rate limiter instance (configurable: 60 requests per minute)
rate_limiter = RateLimiter(max_requests=60, window_seconds=60)


async def verify_api_key(x_api_key: str = Header(None)) -> str:
    """
    Dependency to validate X-API-Key header.
    
    Args:
        x_api_key: The API key from the X-API-Key header.
        
    Returns:
        The validated API key.
        
    Raises:
        HTTPException: 401 if API key is missing or invalid.
    """
    if x_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header is missing",
        )
    
    if x_api_key not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    return x_api_key


async def check_rate_limit(x_api_key: str = Header(None)) -> str:
    """
    Dependency to validate API key and enforce rate limiting.
    
    Args:
        x_api_key: The API key from the X-API-Key header.
        
    Returns:
        The validated API key.
        
    Raises:
        HTTPException: 401 if API key is missing or invalid.
        HTTPException: 429 if rate limit exceeded.
    """
    # First validate the API key
    if x_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header is missing",
        )
    
    if x_api_key not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    # Check rate limit
    if not rate_limiter.is_allowed(x_api_key):
        remaining = rate_limiter.get_remaining(x_api_key)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={
                "X-RateLimit-Limit": str(rate_limiter.max_requests),
                "X-RateLimit-Remaining": str(remaining),
                "Retry-After": str(rate_limiter.window_seconds),
            },
        )
    
    return x_api_key
