from fastapi import APIRouter

from api.dependencies.auth import auth_backend
from core.config import settings
from core.schemas.user import UserCreate, UserRead

from .fastapi_users_routers import fastapi_users

router = APIRouter(
    prefix=settings.api.v1.auth,
    tags=["Auth"],
)

router.include_router(
    router=fastapi_users.get_auth_router(
        auth_backend,
        # requires_verification=True,
    ),
)


router.include_router(
    router=fastapi_users.get_register_router(
        UserRead,
        UserCreate,
    ),
)

router.include_router(
    router=fastapi_users.get_verify_router(UserRead),
)


router.include_router(
    router=fastapi_users.get_reset_password_router(),
)
