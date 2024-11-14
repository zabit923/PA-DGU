from datetime import timedelta

from fastapi import HTTPException
from sqladmin.authentication import AuthenticationBackend
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse

from api.users.service import UserService
from api.users.utils import create_access_token, decode_token, verify_password
from core.database.db import async_session_maker

user_service = UserService()


class AdminAuth(AuthenticationBackend):
    def __init__(self, secret_key: str):
        super().__init__(secret_key=secret_key)

    async def login(self, request: Request) -> bool:
        async with async_session_maker() as session:
            form = await request.form()
            username, password = form["username"], form["password"]

            user = await user_service.get_user_by_username(username, session)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate user.",
                )
            password_valid = verify_password(password, user.password)
            if password_valid:
                if user.is_superuser:
                    token = create_access_token(
                        username=user.username,
                        user_id=user.id,
                        expires_delta=timedelta(hours=24),
                    )
                    request.session.update({"token": token})
                    return True
            return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> RedirectResponse:
        token = request.session.get("token")
        if not token:
            return RedirectResponse(
                request.url_for("admin:login"), status_code=status.HTTP_302_FOUND
            )
        async with async_session_maker() as session:
            token_data = decode_token(token)
            if token_data is None:
                return RedirectResponse(
                    request.url_for("admin:login"), status_code=status.HTTP_302_FOUND
                )
            user = await user_service.get_user_by_username(
                token_data["username"], session
            )
            if not user:
                return RedirectResponse(
                    request.url_for("admin:login"), status_code=status.HTTP_302_FOUND
                )
            return user
