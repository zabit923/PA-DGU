from fastapi import APIRouter

from api.chats.main import router as chat_router
from api.groups.routes import router as groups_router
from api.users.routes import router as users_router

router = APIRouter(prefix="/api/v1")
router.include_router(users_router, tags=["users"])
router.include_router(groups_router, tags=["groups"])
router.include_router(chat_router, tags=["chats"])
