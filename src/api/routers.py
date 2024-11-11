from fastapi import APIRouter

from api.users.router import router as users_router

router = APIRouter(prefix="/api/v1")
router.include_router(users_router, tags=["users"])
