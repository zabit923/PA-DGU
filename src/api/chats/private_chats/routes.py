from typing import List

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.chats.dependencies import authorize_websocket
from api.users.dependencies import get_current_user
from core.database import get_async_session
from core.database.models import User

from .managers import PrivateConnectionManager
from .schemas import PrivateMessageCreate, PrivateMessageRead
from .service import PersonalMessageService

router = APIRouter(prefix="/private-chats")

manager = PrivateConnectionManager()
service = PersonalMessageService()


@router.websocket("/{receiver_id}")
async def private_chat_websocket(
    receiver_id: int,
    websocket: WebSocket,
    user: User = Depends(authorize_websocket),
    session: AsyncSession = Depends(get_async_session),
):
    room = await service.get_or_create_room(
        user1_id=user.id, user2_id=receiver_id, session=session
    )
    await manager.connect(room.id, user.username, websocket)
    try:
        while True:
            try:
                message_data = PrivateMessageCreate(**await websocket.receive_json())
                message = await service.create_message(
                    user.id, room.id, message_data, session
                )
                message = PrivateMessageRead.model_validate(message).model_dump(
                    mode="json"
                )
                await manager.send_message(room.id, message, exclude=user.username)
            except ValueError as e:
                await websocket.send_text(f"Invalid message format: {e}")
                continue
    except WebSocketDisconnect:
        manager.disconnect(room.id, user.username)
    finally:
        if websocket.client_state == "CONNECTED":
            await websocket.close(code=1000)


@router.get(
    "/{receiver_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[PrivateMessageRead],
)
async def get_messages(
    receiver_id: int,
    offset: int = 0,
    limit: int = 50,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> List[PrivateMessageRead]:
    room = await service.get_or_create_room(
        user1_id=user.id, user2_id=receiver_id, session=session
    )
    messages = await service.get_messages(room, offset, limit, session)
    return messages
