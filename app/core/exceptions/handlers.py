import uuid
from datetime import datetime
from typing import Any, Dict, Optional

import pytz
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.websockets import WebSocketDisconnect

from app.core.exceptions import AuthenticationError, BaseAPIException

moscow_tz = pytz.timezone("Europe/Moscow")


def create_error_response(
    status_code: int,
    detail: str,
    error_type: str,
    request_id: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
    flat_structure: bool = False,
) -> JSONResponse:
    if request_id is None:
        request_id = str(uuid.uuid4())

    timestamp = datetime.now(moscow_tz).isoformat()

    headers = {}

    if status_code == 401:
        headers["WWW-Authenticate"] = "Bearer"

    if flat_structure:
        content = {
            "detail": detail,
            "error_type": error_type,
            "status_code": status_code,
            "timestamp": timestamp,
            "request_id": request_id,
            "error": extra,
        }

        if extra:
            for key, value in extra.items():
                content[key] = value
    else:
        content = {
            "success": False,
            "message": None,
            "data": None,
            "error": {
                "detail": detail,
                "error_type": error_type,
                "status_code": status_code,
                "timestamp": timestamp,
                "request_id": request_id,
                "extra": extra,
            },
        }

    return JSONResponse(status_code=status_code, content=content, headers=headers)


async def api_exception_handler(_request: Request, exc: BaseAPIException):
    request_id = exc.extra.get("request_id", None)

    return create_error_response(
        status_code=exc.status_code,
        detail=exc.detail,
        error_type=exc.error_type,
        request_id=request_id,
        extra=exc.extra,
    )


async def http_exception_handler(_request: Request, exc: HTTPException):
    return create_error_response(
        status_code=exc.status_code, detail=str(exc.detail), error_type="http_error"
    )


async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    errors = [{"loc": err["loc"], "msg": err["msg"]} for err in exc.errors()]

    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Ошибка валидации данных",
        error_type="validation_error",
        extra={"errors": errors},
    )


async def websocket_exception_handler(_request: Request, exc: Exception):
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Ошибка WebSocket соединения",
        error_type="websocket_error",
        extra={"error": str(exc)},
    )


async def auth_exception_handler(_request: Request, exc: Exception):
    return create_error_response(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Ошибка авторизации",
        error_type="auth_error",
        extra={"error": str(exc)},
        flat_structure=True,
    )


async def internal_exception_handler(_request: Request, exc: Exception):
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Внутренняя ошибка сервера",
        error_type="internal_error",
        extra={"error": str(exc)},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(BaseAPIException, api_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(WebSocketDisconnect, websocket_exception_handler)
    app.add_exception_handler(AuthenticationError, auth_exception_handler)
    app.add_exception_handler(Exception, internal_exception_handler)
