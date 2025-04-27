import json
import logging
from typing import Any, Dict, Optional

from fastapi import Depends

from api.chats.common import authorize_socket, sio_server
from api.chats.group_chats.schemas import GroupMessageCreate, GroupMessageRead
from api.chats.group_chats.service import GroupChatService
from api.groups.service import GroupService, group_service_factory
from api.notifications.service import NotificationService
from api.users.service import UserService, user_service_factory
from core.database.models import User

logger = logging.getLogger(__name__)
GROUP_NAMESPACE = "/groups"


@sio_server.on("connect", namespace=GROUP_NAMESPACE)
async def connect(
    sid: str,
    environ: Dict[str, Any],
    user_service: UserService = Depends(user_service_factory),
) -> None:
    headers = dict(environ.get("asgi.scope", {}).get("headers", []))
    authorization = headers.get(b"authorization")
    if not authorization:
        logger.warning("No Authorization header in group namespace!")
        return False
    token = authorization.decode().split(" ")[1]
    user = await authorize_socket(token, user_service)
    environ["user"] = user
    sio_server.environ[sid] = {"user": user}
    logger.info(f"[GROUP] Connected: {sid} user={user.username}")


@sio_server.on("join_group", namespace=GROUP_NAMESPACE)
async def join_group(
    sid: str,
    data: Any,
    group_service: GroupService = Depends(group_service_factory),
    chat_service: GroupChatService = Depends(group_service_factory),
) -> None:
    try:
        if isinstance(data, str):
            data = json.loads(data)
        elif not isinstance(data, dict):
            raise ValueError("Invalid data format")

        group_id = data.get("group_id")
        if group_id is None:
            raise ValueError("Missing group_id")

        user: User = sio_server.environ[sid]["user"]
        logger.warning(data)
        if not await group_service.contrained_user_in_group(user, group_id):
            logger.warning(
                f"[GROUP] Join failed: user {user.username} not in group {group_id}"
            )
            await sio_server.emit(
                "error", {"message": "You are not a member of this group"}, room=sid
            )
            return

        await sio_server.manager.connect(sid, group_id, user.username)
        await chat_service.update_online_status(user)
        await sio_server.emit("joined", {"group_id": group_id}, room=sid)
        logger.info(f"[GROUP] User {user.username} joined group {group_id}")

    except ValueError as e:
        logger.warning(f"[GROUP] Bad join request: {e}")
        await sio_server.emit("error", {"message": str(e)}, room=sid)

    except Exception as e:
        logger.error(f"[GROUP] Unexpected error on join: {e}", exc_info=True)
        await sio_server.emit("error", {"message": "Internal server error"}, room=sid)


@sio_server.on("send_message", namespace=GROUP_NAMESPACE)
async def send_message(
    sid: str,
    data: Dict[str, Any],
    chat_service: GroupChatService = Depends(group_service_factory),
    notification_service: NotificationService = Depends(group_service_factory),
) -> None:
    user: User = sio_server.environ[sid]["user"]
    group_id: int = data["group_id"]
    message_data = GroupMessageCreate(**data)
    message = await chat_service.create_message(message_data, user, group_id)
    await notification_service.create_group_message_notification(message, chat_service)
    serialized = GroupMessageRead.model_validate(message).model_dump(mode="json")
    await sio_server.manager.send_message(
        group_id, "new_message", serialized, skip_sid=sid
    )


@sio_server.on("typing", namespace=GROUP_NAMESPACE)
async def typing(
    sid: str,
    data: Dict[str, Any],
) -> None:
    user: User = sio_server.environ[sid]["user"]
    group_id: int = data["group_id"]
    is_typing: bool = data.get("is_typing", False)
    await sio_server.manager.notify_typing(group_id, user.username, is_typing)


@sio_server.on("disconnect", namespace=GROUP_NAMESPACE)
async def disconnect(
    sid: str,
    chat_service: GroupChatService = Depends(group_service_factory),
) -> None:
    user: Optional[User] = sio_server.environ.get(sid, {}).get("user")
    if user:
        for group_id, users in sio_server.manager.rooms_users.items():
            if user.username in users:
                await sio_server.manager.disconnect(sid, group_id, user.username)
        await chat_service.update_online_status(user)
    logger.info(f"[GROUP] Disconnected: {sid}")
