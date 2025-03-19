from jose import JWTError
from sqlalchemy.future import select
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    BaseUser,
)

from api.users.utils import decode_token
from core.database.db import async_session_maker
from core.database.models import User


class CustomUser(BaseUser):
    def __init__(self, id: int):
        self.id = id

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return str(self.id)


class HTTPAuthenticationMiddleware(AuthenticationBackend):
    async def authenticate(self, request):
        if "Authorization" not in request.headers:
            return
        auth = request.headers["Authorization"]
        try:
            scheme, token = auth.split()
            if scheme.lower() != "bearer":
                return
            decoded = decode_token(token)
        except (ValueError, JWTError) as exc:
            raise AuthenticationError("Invalid JWT Token.") from exc

        user_id: int = decoded.get("user_id")

        if not user_id:
            raise AuthenticationError("Token payload is invalid.")

        async with async_session_maker() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
        if not user:
            raise AuthenticationError("User not found.")
        return AuthCredentials(["authenticated"]), CustomUser(user_id)
