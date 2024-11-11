import logging

import uvicorn
from fastapi import FastAPI
from sqladmin import Admin
from starlette.middleware.sessions import SessionMiddleware

from admin import AdminAuth, UserAdmin
from api.routers import router as api_router
from config import settings
from core.auth.db import engine
from core.auth.users import fastapi_users, get_user_manager

logging.basicConfig(
    format=settings.logging.log_format,
)


app = FastAPI()
app.include_router(
    api_router,
)
app.add_middleware(SessionMiddleware, secret_key=settings.secret.secret_key)


user_manager_instance = get_user_manager()
admin_authentication_backend = AdminAuth(
    fastapi_users=fastapi_users, user_manager=user_manager_instance
)
admin = Admin(
    app=app, engine=engine, authentication_backend=admin_authentication_backend
)

admin.add_view(UserAdmin)

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
