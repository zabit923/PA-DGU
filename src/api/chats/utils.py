from functools import wraps

from jose import JWTError
from starlette.authentication import AuthenticationError
from starlette.websockets import WebSocket

from api.users.service import UserService
from core.database.db import async_session_maker
from core.database.models import User
from core.security.jwt import decode_token

user_service = UserService()


async def authorize_websocket(websocket: WebSocket) -> User | None:
    token = websocket.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        await websocket.close(code=4001)
        return None
    try:
        token = token.split()[1]
        decoded_token = decode_token(token)
        user_id = decoded_token.get("user_id")
        if not user_id:
            raise AuthenticationError("Token payload is invalid.")

        async with async_session_maker() as session:
            user = await user_service.get_user_by_id(user_id, session)

        if not user:
            raise AuthenticationError("User not found.")

        return user
    except (ValueError, JWTError, AuthenticationError):
        await websocket.close(code=4001)
        return None


def websocket_auth_required(func):
    @wraps(func)
    async def wrapper(websocket: WebSocket):
        user = await authorize_websocket(websocket)
        if user is None:
            return
        return await func(websocket)

    return wrapper
