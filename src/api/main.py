from fastapi import APIRouter

from api.chats.main import router as chat_router
from api.exams.routes import router as exams_router
from api.groups.routes import router as groups_router
from api.materials.routes import router as materials_router
from api.users.routes import router as users_router

router = APIRouter(prefix="/api/v1")
router.include_router(users_router, tags=["users"])
router.include_router(groups_router, tags=["groups"])
router.include_router(chat_router, tags=["chats"])
router.include_router(materials_router, tags=["materials"])
router.include_router(exams_router, tags=["exams"])
