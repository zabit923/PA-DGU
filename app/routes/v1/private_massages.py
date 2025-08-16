from json import JSONDecodeError
from typing import List

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.routes.base import BaseRouter
from app.models import User
from app.core.managers.private_websocket import PrivateConnectionManager
from app.core.dependencies import authorize_websocket, get_db_session
from app.services.v1.private_chats.service import PrivateMessageService
from app.schemas import (
    PrivateMessageResponseSchema,
    PrivateMessageCreateSchema,
    PrivateMessageListResponseSchema,
    RoomResponseSchema,
    PaginationParams,
    PrivateMessageUpdateSchema
)
from app.services.v1.notifications.service import NotificationService
from app.core.security.auth import get_current_user

websocket_manager = PrivateConnectionManager()


class PrivateMessageRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="chats/private-chats", tags=["Private Chats"])

    def configure(self):
        @self.router.websocket("/{receiver_id}")
        async def private_chat_websocket(
            receiver_id: int,
            websocket: WebSocket,
            user: User = Depends(authorize_websocket),
            session: AsyncSession = Depends(get_db_session),
        ):
            room = await PrivateMessageService(session).get_or_create_room(
                user_id1=user.id,
                user_id2=receiver_id,
                user=user
            )
            await websocket_manager.connect(room.id, user.username, websocket)
            await PrivateMessageService(session).update_online_status(user)
            try:
                while True:
                    try:
                        message_data = await websocket.receive_json()

                        if (
                            "action" in message_data
                            and message_data["action"] == "typing"
                        ):
                            is_typing = message_data.get("is_typing", False)
                            await websocket_manager.notify_typing_status(
                                room.id, user.username, is_typing
                            )
                            continue
                        if (
                            "action" in message_data
                            and message_data["action"] == "read"
                        ):
                            message_ids = message_data.get("message_ids", [])
                            await PrivateMessageService(session).set_incoming_messages_is_read_bulk(
                                user.id, message_ids
                            )
                            continue

                        message_data = PrivateMessageCreateSchema(**message_data)
                        message = await PrivateMessageService(session).create_message(
                            user, room.id, message_data
                        )

                        await NotificationService(
                            session
                        ).create_private_message_notification(message)
                        message = PrivateMessageResponseSchema.model_validate(message).model_dump(
                            mode="json"
                        )
                        await websocket_manager.send_message(
                            room.id,
                            message,
                            exclude=user.username
                        )
                    except (JSONDecodeError, AttributeError) as e:
                        await websocket_manager.send_error(e, websocket)
                        continue
                    except ValueError as e:
                        await websocket_manager.send_error(
                            "Could not validate incoming message", websocket
                        )
            except WebSocketDisconnect:
                await PrivateMessageService(session).update_online_status(user)
                websocket_manager.disconnect(room.id, user.username)

        @self.router.get(
            "/get-my-rooms", status_code=status.HTTP_200_OK, response_model=List[RoomResponseSchema]
        )
        async def get_my_rooms(
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ) -> List[RoomResponseSchema]:
            rooms = await PrivateMessageService(session).get_my_rooms(user)
            return rooms

        @self.router.get(
            "/{receiver_id}",
            status_code=status.HTTP_200_OK,
            response_model=PrivateMessageListResponseSchema,
        )
        async def get_messages(
            receiver_id: int,
            skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
            limit: int = Query(
                10, ge=1, le=100, description="Количество элементов на странице"
            ),
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ) -> PrivateMessageListResponseSchema:
            """
            ### Args:
            * **skip**: Количество пропускаемых элементов
            * **limit**: Количество элементов на странице (от 1 до 100)
            """
            room = await PrivateMessageService(session).get_or_create_room(
                user_id1=user.id,
                user_id2=receiver_id,
                user=user
            )
            pagination = PaginationParams(skip=skip, limit=limit)
            messages, total = await PrivateMessageService(session).get_messages(user, user.id, room, pagination)
            page = {
                "items": messages,
                "total": total,
                "page": pagination.page,
                "size": pagination.limit,
            }
            return PrivateMessageListResponseSchema(data=page)

        @self.router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete_message(
            message_id: int,
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            message = await PrivateMessageService(session).get_message_by_id(message_id)
            await PrivateMessageService(session).delete_message(message_id, user)
            await websocket_manager.notify_deletion(message.room_id, message_id)
            return

        @self.router.patch(
            "/{message_id}",
            status_code=status.HTTP_200_OK,
            response_model=PrivateMessageResponseSchema,
        )
        async def update_message(
            message_id: int,
            message_data: PrivateMessageUpdateSchema,
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            message = await PrivateMessageService(session).get_message_by_id(message_id)
            updated_message = await PrivateMessageService(session).update_message(message, message_data, user)
            await websocket_manager.notify_update(
                message.room_id, message_id, message_data.text, message.created_at
            )
            return updated_message
