import socketio
from fastapi import HTTPException
from fastapi.params import Depends
from starlette import status

from api.users.service import UserService, user_service_factory
from api.users.utils import decode_token
from core.database.models import User

sio_server = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


async def authorize_socket(
    token: str, user_service: UserService = Depends(user_service_factory)
) -> User:
    try:
        payload = decode_token(token)
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
            )
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )
        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
