from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import ConfigDict

from app.schemas.v1.base import BaseResponseSchema, BaseSchema
from app.schemas.v1.users import UserShortSchema


class PrivateMessageResponseSchema(BaseSchema):
    text: str
    sender: "UserShortSchema"
    room_id: int
    is_readed: bool

    model_config = ConfigDict(from_attributes=True)


class PrivateMessageListResponseSchema(BaseResponseSchema):
    message: str = "Список сообщений успешно получен"
    data: Dict[str, Any]


class RoomResponseSchema(BaseSchema):
    last_message: Optional["PrivateMessageResponseSchema"]
    members: List["UserShortSchema"]


PrivateMessageResponseSchema.model_rebuild()
RoomResponseSchema.model_rebuild()
