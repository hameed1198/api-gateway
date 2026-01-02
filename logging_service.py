"""
Request Logging and Auditing for the API Gateway.

Tracks all API requests for monitoring, debugging, and compliance.
"""

import time
from dataclasses import dataclass, field
from typing import Optional
from collections import deque


@dataclass
class RequestLog:
    """Represents a logged API request."""
    id: str
    timestamp: float
    partner_id: str
    partner_name: str
    method: str
    path: str
    service: str
    status_code: int
    response_time_ms: float
    client_ip: Optional[str] = None
    error_message: Optional[str] = None


class RequestLogger:
    """
    In-memory request logger for auditing.
    
    In production, this would write to a database or logging service.
    """
    
    def __init__(self, max_logs: int = 10000):
        """
        Initialize the request logger.
        
        Args:
            max_logs: Maximum number of logs to keep in memory.
        """
        self._logs: deque[RequestLog] = deque(maxlen=max_logs)
        self._counter = 0
    
    def log_request(
        self,
        partner_id: str,
        partner_name: str,
        method: str,
        path: str,
        service: str,
        status_code: int,
        response_time_ms: float,
        client_ip: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> RequestLog:
        """Log an API request."""
        self._counter += 1
        log = RequestLog(
            id=f"req-{self._counter:08d}",
            timestamp=time.time(),
            partner_id=partner_id,
            partner_name=partner_name,
            method=method,
            path=path,
            service=service,
            status_code=status_code,
            response_time_ms=response_time_ms,
            client_ip=client_ip,
            error_message=error_message
        )
        self._logs.append(log)
        return log
    
    def get_recent_logs(self, limit: int = 100) -> list[RequestLog]:
        """Get the most recent logs."""
        return list(self._logs)[-limit:]
    
    def get_logs_by_partner(self, partner_id: str, limit: int = 100) -> list[RequestLog]:
        """Get logs for a specific partner."""
        partner_logs = [log for log in self._logs if log.partner_id == partner_id]
        return partner_logs[-limit:]
    
    def get_stats(self) -> dict:
        """Get aggregate statistics."""
        if not self._logs:
            return {
                "total_requests": 0,
                "requests_by_service": {},
                "requests_by_partner": {},
                "error_count": 0,
                "avg_response_time_ms": 0
            }
        
        logs = list(self._logs)
        
        # Count by service
        by_service: dict[str, int] = {}
        for log in logs:
            by_service[log.service] = by_service.get(log.service, 0) + 1
        
        # Count by partner
        by_partner: dict[str, int] = {}
        for log in logs:
            by_partner[log.partner_name] = by_partner.get(log.partner_name, 0) + 1
        
        # Error count
        error_count = sum(1 for log in logs if log.status_code >= 400)
        
        # Average response time
        avg_response_time = sum(log.response_time_ms for log in logs) / len(logs)
        
        return {
            "total_requests": len(logs),
            "requests_by_service": by_service,
            "requests_by_partner": by_partner,
            "error_count": error_count,
            "avg_response_time_ms": round(avg_response_time, 2)
        }


# Global request logger instance
request_logger = RequestLogger()
