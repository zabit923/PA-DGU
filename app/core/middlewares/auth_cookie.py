from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class AuthCookieMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        access_token = request.cookies.get("access_token")

        if access_token and not request.headers.get("authorization"):
            request.headers.__dict__["_list"].append(
                (b"authorization", f"Bearer {access_token}".encode())
            )

        response = await call_next(request)
        return response
