from typing import List

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.chats.dependencies import authorize_websocket
from api.users.dependencies import get_current_user
from core.database import get_async_session
from core.database.models import User

from .managers import PrivateConnectionManager
from .schemas import (
    PrivateMessageCreate,
    PrivateMessageRead,
    PrivateMessageUpdate,
    RoomRead,
)
from .service import PersonalMessageService

router = APIRouter(prefix="/private-chats")

manager = PrivateConnectionManager()
message_service = PersonalMessageService()


@router.websocket("/{receiver_id}")
async def private_chat_websocket(
    receiver_id: int,
    websocket: WebSocket,
    user: User = Depends(authorize_websocket),
    session: AsyncSession = Depends(get_async_session),
):
    room = await message_service.get_or_create_room(
        user1_id=user.id, user2_id=receiver_id, session=session
    )
    await manager.connect(room.id, user.username, websocket)
    try:
        while True:
            try:
                message_data = await websocket.receive_json()

                if "action" in message_data and message_data["action"] == "typing":
                    is_typing = message_data.get("is_typing", False)
                    await manager.notify_typing_status(
                        room.id, user.username, is_typing
                    )
                    continue

                message_data = PrivateMessageCreate(**message_data)
                message = await message_service.create_message(
                    user, room.id, message_data, session
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
    "/get-my-rooms", status_code=status.HTTP_200_OK, response_model=List[RoomRead]
)
async def get_my_rooms(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> List[RoomRead]:
    rooms = await message_service.get_my_rooms(user, session)
    return rooms


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
    room = await message_service.get_or_create_room(
        user1_id=user.id, user2_id=receiver_id, session=session
    )
    messages = await message_service.get_messages(room, offset, limit, session)
    return messages


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    message = await message_service.get_message_by_id(message_id, session)
    if message.sender != user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this message.",
        )
    await message_service.delete_message(message_id, session)
    await manager.notify_deletion(message.room_id, message_id)
    return {"detail": "Message deleted successfully."}


@router.patch(
    "/{message_id}",
    status_code=status.HTTP_200_OK,
    response_model=PrivateMessageRead,
)
async def update_message(
    message_id: int,
    message_data: PrivateMessageUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    message = await message_service.get_message_by_id(message_id, session)
    if message.sender != user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this message.",
        )
    updated_message = await message_service.update_message(
        message, message_data, session
    )
    await manager.notify_update(message.room_id, message_id)
    return updated_message
