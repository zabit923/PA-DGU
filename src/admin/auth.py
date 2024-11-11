from datetime import timedelta

from sqladmin.authentication import AuthenticationBackend
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse

from api.users.dependencies import authenticate_user, create_token_access
from config import settings
from core.database.db import async_session_maker
from core.utils.protect import protected_endpoint

SECRET = settings.secret.secret_key
ALGORITHM = "HS256"


class AdminAuth(AuthenticationBackend):
    def __init__(self, secret_key: str = SECRET):
        super().__init__(secret_key=secret_key)

    async def login(self, request: Request) -> bool:
        async with async_session_maker() as session:
            form = await request.form()
            username, password = form["username"], form["password"]

            user = await authenticate_user(username, password, session)
            if user and user.is_superuser:
                token = await create_token_access(
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
            user = await protected_endpoint(token, session)
            if not user:
                return RedirectResponse(
                    request.url_for("admin:login"), status_code=status.HTTP_302_FOUND
                )
            return user
