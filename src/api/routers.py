from fastapi import APIRouter

from api.chats.routers import router as chat_router
from api.exams.routers import router as exams_router
from api.groups.routers import router as groups_router
from api.materials.routers import router as materials_router
from api.news.routers import router as news_router
from api.notifications.routers import router as notification_router
from api.users.routers import router as users_router

router = APIRouter(prefix="/api/v1")
router.include_router(users_router, tags=["users"])
router.include_router(groups_router, tags=["groups"])
router.include_router(chat_router, tags=["chats"])
router.include_router(materials_router, tags=["materials"])
router.include_router(exams_router, tags=["exams"])
router.include_router(notification_router, tags=["notification"])
router.include_router(news_router, tags=["news"])
