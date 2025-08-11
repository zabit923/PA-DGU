from fastapi import Depends, Query
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.authentication import AuthenticationError
from starlette.websockets import WebSocket

from app.core.dependencies import get_db_session
from app.core.exceptions import UserNotFoundError
from app.core.security.token import TokenManager
from app.models import User
from app.services.v1.users.service import UserService


async def authorize_websocket(
    websocket: WebSocket,
    token: str = Query(None),
    session: AsyncSession = Depends(get_db_session),
) -> User | None:
    if not token:
        await websocket.close(code=4001)
        return None
    try:
        decoded_token = TokenManager.verify_token(token)
        user_id = decoded_token.get("user_id")
        user = await UserService(session).get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError("Пользователь не найден")
        return user
    except (ValueError, JWTError, AuthenticationError):
        await websocket.close(code=4001)
        return None
