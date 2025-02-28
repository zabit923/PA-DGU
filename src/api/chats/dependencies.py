from fastapi import Depends
from jose import JWTError
from starlette.authentication import AuthenticationError
from starlette.websockets import WebSocket

from api.users.service import UserService, user_service_factory
from core.database.models import User
from core.security.jwt import decode_token


async def authorize_websocket(
    websocket: WebSocket, user_service: UserService = Depends(user_service_factory)
) -> User | None:
    token = websocket.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        await websocket.close(code=4001)
        return None
    try:
        token = token.split()[1]
        decoded_token = decode_token(token)
        user_id = decoded_token.get("user_id")
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise AuthenticationError("User not found.")
        return user
    except (ValueError, JWTError, AuthenticationError):
        await websocket.close(code=4001)
        return None
