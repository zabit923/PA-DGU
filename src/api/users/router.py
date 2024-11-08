from fastapi import APIRouter

from core.auth.users import auth_backend, fastapi_users

from .schemas import UserCreate, UserRead

router = APIRouter(
    prefix="/api/v1",
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
