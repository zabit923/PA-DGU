import logging

import socketio
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware

from admin.auth import AdminAuth
from api.chats.common import sio_server
from api.routers import router as api_router
from config import settings, static_dir
from core.auth.jwt import HTTPAuthenticationMiddleware
from core.database.db import engine

logging.basicConfig(
    format=settings.logging.log_format,
)


origins = [
    "http://localhost:8000",
    "http://localhost:5173",
    "ws://127.0.0.1:8000",
    "ws://127.0.0.1:5173",
    "wss://defe-89-208-103-117.ngrok-free.app",
    "https://defe-89-208-103-117.ngrok-free.app",
]


app = FastAPI()
app.include_router(
    api_router,
)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

admin_auth = AdminAuth(secret_key=settings.secret.secret_key)
admin = Admin(app=app, engine=engine, authentication_backend=admin_auth)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthenticationMiddleware, backend=HTTPAuthenticationMiddleware())

combined_app = socketio.ASGIApp(
    socketio_server=sio_server,
    other_asgi_app=app,
)

if __name__ == "__main__":
    uvicorn.run(
        "app:combined_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
