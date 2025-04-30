from fastapi import Depends, Query
from starlette.websockets import WebSocket

from api.users.service import UserService, user_service_factory
from core.auth.jwt import decode_token
from core.database.models import User


async def authorize_websocket(
    websocket: WebSocket,
    token: str = Query(None),
    user_service: UserService = Depends(user_service_factory),
) -> User | None:
    if not token:
        await websocket.close(code=4001)
        return None
    decoded_token = decode_token(token)
    user_id = decoded_token.get("user_id")
    user = await user_service.get_user_by_id(user_id)
    if not user:
        await websocket.close(code=4003)
        return None
    return user
