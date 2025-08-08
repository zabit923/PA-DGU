from json import JSONDecodeError
from typing import List

from core.dependencies import authorize_websocket, get_db_session
from core.managers.group_websocket import GroupConnectionManager
from core.security.auth import get_current_user
from fastapi import Depends, Query, WebSocketException
from routes.base import BaseRouter
from services.v1.group_chats.service import GroupMessageService
from services.v1.groups.service import GroupService
from services.v1.notifications.service import NotificationService
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.models import User
from app.schemas import (
    GroupMessageCheckResponseSchema,
    GroupMessageCreateSchema,
    GroupMessageListResponseSchema,
    GroupMessageResponseSchema,
    GroupMessageUpdate,
    PaginationParams,
)


class GroupMessageRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="/chats/groups", tags=["Group Chats"])

    def configure(self):
        @self.router.websocket("/{group_id}")
        async def group_chat_websocket(
            group_id: int,
            websocket: WebSocket,
            user: User = Depends(authorize_websocket),
            session: AsyncSession = Depends(get_db_session),
        ):
            group = await GroupService(session).get_group(group_id)
            if not group:
                raise WebSocketException(
                    code=status.WS_1008_POLICY_VIOLATION, reason="Group not found."
                )
            if user not in group.members:
                raise WebSocketException(
                    code=status.WS_1008_POLICY_VIOLATION,
                    reason="Пользователь не состоит в группе.",
                )
            await GroupConnectionManager().connect(group_id, user.username, websocket)
            await GroupMessageService(session).update_online_status(user)
            try:
                while True:
                    try:
                        message_data = await websocket.receive_json()

                        if (
                            "action" in message_data
                            and message_data["action"] == "typing"
                        ):
                            is_typing = message_data.get("is_typing", False)
                            await GroupConnectionManager().notify_typing_status(
                                group_id, user.username, is_typing
                            )
                            continue
                        if (
                            "action" in message_data
                            and message_data["action"] == "read"
                        ):
                            message_ids = message_data.get("message_ids", [])
                            await GroupMessageService(
                                session
                            ).set_incoming_messages_as_read(user.id, message_ids)
                            continue

                        message_data = GroupMessageCreateSchema(**message_data)
                        message = await GroupMessageService(session).create_message(
                            message_data, user, group_id
                        )
                        await NotificationService(
                            session
                        ).create_group_message_notification(message)
                        message = GroupMessageResponseSchema.model_validate(
                            message
                        ).model_dump(mode="json")
                        await GroupConnectionManager().broadcast(
                            group_id, message, user.username
                        )
                    except (JSONDecodeError, AttributeError):
                        await GroupConnectionManager().send_error(
                            "Wrong message format", websocket
                        )
                        continue
                    except ValueError:
                        await GroupConnectionManager().send_error(
                            "Could not validate incoming message", websocket
                        )
            except WebSocketDisconnect:
                await GroupMessageService(session).update_online_status(user)
                GroupConnectionManager().disconnect(group_id, user.username)

        @self.router.get(
            "/{group_id}",
            status_code=status.HTTP_200_OK,
            response_model=GroupMessageListResponseSchema,
        )
        async def get_messages(
            group_id: int,
            skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
            limit: int = Query(
                10, ge=1, le=100, description="Количество элементов на странице"
            ),
            user: User = Depends(get_db_session),
            session: AsyncSession = Depends(get_db_session),
        ) -> GroupMessageListResponseSchema:
            """
            ### Args:
            * **skip**: Количество пропускаемых элементов
            * **limit**: Количество элементов на странице (от 1 до 100)
            """
            group = await GroupService(session).get_group(group_id)
            pagination = PaginationParams(skip=skip, limit=limit)
            messages, total = await GroupMessageService(session).get_messages(
                group, user, pagination
            )
            page = {
                "items": messages,
                "total": total,
                "page": pagination.page,
                "size": pagination.limit,
            }
            return GroupMessageListResponseSchema(data=page)

        @self.router.get(
            "/get-checks/{message_id}",
            status_code=status.HTTP_200_OK,
            response_model=List[GroupMessageCheckResponseSchema],
        )
        async def get_users_who_check_message(
            message_id: int,
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ) -> List[GroupMessageCheckResponseSchema]:
            message = await GroupMessageService(session).get_message_by_id(message_id)
            return await GroupMessageService(session).get_message_checks(message, user)

        @self.router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete_message(
            message_id: int,
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            message = await GroupMessageService(session).get_message_by_id(message_id)
            await GroupMessageService(session).delete_message(message_id, user)
            await GroupConnectionManager().notify_deletion(message.group_id, message_id)
            return

        @self.router.patch(
            "/{message_id}",
            status_code=status.HTTP_200_OK,
            response_model=GroupMessageResponseSchema,
        )
        async def update_message(
            message_id: int,
            message_data: GroupMessageUpdate,
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            message = await GroupMessageService(session).get_message_by_id(message_id)
            updated_message = await GroupMessageService(session).update_message(
                message, message_data, user
            )
            await GroupConnectionManager().notify_update(
                message.group_id, message_id, message_data.text, message.created_at
            )
            return updated_message
