import logging

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware

from admin import (
    AdminAuth,
    AnswerAdmin,
    ChoiseQuestionAdmin,
    ExamAdmin,
    GroupAdmin,
    GroupMessageAdmin,
    NotificationAdmin,
    PassedChoiseAnswersAdmin,
    PassedTextAnswersAdmin,
    PersonalMessageAdmin,
    ResultAdmin,
    RoomAdmin,
    TextQuestionAdmin,
    UserAdmin,
)
from admin.lecture import LectureAdmin
from api.routers import router as api_router
from config import settings, static_dir
from core.database.db import engine
from core.security.jwt import HTTPAuthenticationMiddleware

logging.basicConfig(
    format=settings.logging.log_format,
)


origins = ["http://localhost:8000", "http://localhost:5173", "ws://127.0.0.1:8000"]


app = FastAPI()
app.include_router(
    api_router,
)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

admin_auth = AdminAuth(secret_key=settings.secret.secret_key)
admin = Admin(app=app, engine=engine, authentication_backend=admin_auth)
admin.add_view(UserAdmin)
admin.add_view(GroupAdmin)
admin.add_view(GroupMessageAdmin)
admin.add_view(PersonalMessageAdmin)
admin.add_view(RoomAdmin)
admin.add_view(LectureAdmin)
admin.add_view(ExamAdmin)
admin.add_view(ChoiseQuestionAdmin)
admin.add_view(TextQuestionAdmin)
admin.add_view(AnswerAdmin)
admin.add_view(ResultAdmin)
admin.add_view(NotificationAdmin)
admin.add_view(PassedChoiseAnswersAdmin)
admin.add_view(PassedTextAnswersAdmin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthenticationMiddleware, backend=HTTPAuthenticationMiddleware())

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
