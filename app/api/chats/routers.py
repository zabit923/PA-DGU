from api.chats.group_chats.routers import router as group_chat_router
from api.chats.private_chats.routers import router as private_chat_router
from fastapi import APIRouter

router = APIRouter(prefix="/chats")
router.include_router(group_chat_router, tags=["group_chats"])
router.include_router(private_chat_router, tags=["private_chats"])
