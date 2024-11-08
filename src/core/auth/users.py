from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase

from config import settings
from core.database.models import User

from .db import get_users_db

SECRET = settings.secret.secret_key

# __________________________________________________________________________________________________


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.secret.reset_password_token_secret
    verification_token_secret = settings.secret.verification_token_secret


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_users_db)):
    yield UserManager(user_db)


# __________________________________________________________________________________________________

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600 * 24)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# __________________________________________________________________________________________________

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
current_active_superuser = fastapi_users.current_user(active=True, superuser=True)
