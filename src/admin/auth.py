from fastapi_users import FastAPIUsers
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from config import settings
from core.auth.users import UserManager


class AdminAuth(AuthenticationBackend):
    def __init__(self, fastapi_users: FastAPIUsers, user_manager: UserManager):
        self.fastapi_users = fastapi_users
        self.user_manager = user_manager
        super().__init__(secret_key=settings.secret.secret_key)

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        user = await self.user_manager.authenticate(
            credentials={"username": username, "password": password}
        )

        if user and user.is_superuser:
            request.session.update({"token": str(user.id)})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False

        user = await self.user_manager.get(token)
        return user is not None and user.is_superuser
