import logging

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.exceptions import BaseAPIException
from app.core.settings import settings

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if getattr(settings, "logging_level", "INFO") == "DEBUG":
            logger.debug("Request path: %s", request.url.path)
            logger.debug("Headers: %s", request.headers)

        try:
            response = await call_next(request)
            return response
        except BaseAPIException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code, content={"detail": str(e.detail)}
            )
