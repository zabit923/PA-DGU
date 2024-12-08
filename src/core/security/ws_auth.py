from functools import wraps

from jose import JWTError
from starlette.websockets import WebSocket

from core.security.jwt import decode_token


async def authorize_websocket(websocket: WebSocket):
    token = websocket.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        await websocket.close(code=4001)
        return None

    try:
        token = token.split()[1]
        decoded_token = decode_token(token)
        return decoded_token
    except (IndexError, JWTError):
        await websocket.close(code=4001)
        return None


def websocket_auth_required(func):
    @wraps(func)
    async def wrapper(websocket: WebSocket, *args, **kwargs):
        user = await authorize_websocket(websocket)
        if user is None:
            return
        return await func(websocket, user, *args, **kwargs)

    return wrapper
