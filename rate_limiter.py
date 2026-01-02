"""
Rate Limiting for the API Gateway.

Implements per-partner rate limiting with configurable limits.
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class RateLimitState:
    """Tracks request timestamps for rate limiting."""
    timestamps: list[float] = field(default_factory=list)


class RateLimiter:
    """
    Per-partner rate limiter using sliding window algorithm.
    
    Each partner can have a different rate limit based on their tier.
    """
    
    def __init__(self, window_seconds: int = 60):
        """
        Initialize the rate limiter.
        
        Args:
            window_seconds: Time window in seconds (default: 60 for per-minute limiting).
        """
        self.window_seconds = window_seconds
        self._requests: dict[str, RateLimitState] = defaultdict(RateLimitState)
    
    def is_allowed(self, partner_id: str, max_requests: int) -> bool:
        """
        Check if a request is allowed for the given partner.
        
        Args:
            partner_id: The partner's unique identifier.
            max_requests: Maximum requests allowed for this partner.
            
        Returns:
            True if the request is allowed, False if rate limit exceeded.
        """
        current_time = time.time()
        state = self._requests[partner_id]
        
        # Remove timestamps outside the current window
        cutoff_time = current_time - self.window_seconds
        state.timestamps = [ts for ts in state.timestamps if ts > cutoff_time]
        
        # Check if under the limit
        if len(state.timestamps) >= max_requests:
            return False
        
        # Record this request
        state.timestamps.append(current_time)
        return True
    
    def get_remaining(self, partner_id: str, max_requests: int) -> int:
        """Get the number of remaining requests for a partner."""
        current_time = time.time()
        state = self._requests[partner_id]
        cutoff_time = current_time - self.window_seconds
        valid_timestamps = [ts for ts in state.timestamps if ts > cutoff_time]
        return max(0, max_requests - len(valid_timestamps))
    
    def get_reset_time(self, partner_id: str) -> int:
        """Get seconds until the rate limit window resets."""
        state = self._requests[partner_id]
        if not state.timestamps:
            return 0
        oldest = min(state.timestamps)
        reset_at = oldest + self.window_seconds
        return max(0, int(reset_at - time.time()))


# Global rate limiter instance
rate_limiter = RateLimiter(window_seconds=60)
