import logging
import time
from typing import Dict, Optional, Tuple

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import RateLimitExceededError


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        limit: int = 100,
        window: int = 60,
        exclude_paths: Optional[list] = None,
    ):
        super().__init__(app)
        self.limit = limit
        self.window = window
        self.exclude_paths = exclude_paths or []
        self.requests: Dict[str, Tuple[int, float]] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if any(path.startswith(exclude_path) for exclude_path in self.exclude_paths):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"

        current_time = time.time()

        if client_ip in self.requests:
            count, start_time = self.requests[client_ip]

            if current_time - start_time > self.window:
                self.requests[client_ip] = (1, current_time)
            else:
                count += 1
                self.requests[client_ip] = (count, start_time)

                if count > self.limit:
                    self.logger.warning(
                        f"Превышен лимит запросов для IP {client_ip}",
                        extra={
                            "client_ip": client_ip,
                            "path": path,
                            "method": request.method,
                            "count": count,
                            "limit": self.limit,
                            "window": self.window,
                        },
                    )

                    reset_time = int(start_time + self.window - current_time)

                    raise RateLimitExceededError(reset_time=reset_time)
        else:
            self.requests[client_ip] = (1, current_time)

        response = await call_next(request)

        if client_ip in self.requests:
            count, _ = self.requests[client_ip]
            response.headers["X-RateLimit-Limit"] = str(self.limit)
            response.headers["X-RateLimit-Remaining"] = str(max(0, self.limit - count))
            response.headers["X-RateLimit-Reset"] = str(
                int(self.window - (current_time - self.requests[client_ip][1]))
            )

        return response
