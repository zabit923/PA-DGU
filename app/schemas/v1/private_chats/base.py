from typing import List

from pydantic import ConfigDict, Field

from app.schemas.v1.base import BaseSchema
from app.schemas.v1.groups import GroupShortResponseSchema
from app.schemas.v1.users import UserShortSchema
from .response import PrivateMessageResponseSchema, RoomResponseSchema


class RoomDataSchema(BaseSchema):
    messages: List["PrivateMessageResponseSchema"]
    members: List["UserShortSchema"]


class PrivateMessageDataSchema(BaseSchema):
    room_id: int = Field(
        description="ID комнаты",
    )
    sender_id: int = Field(
        description="ID отправителя сообщения.",
    )
    text: str = Field(
        description="Текст сообщения.",
    )
    is_readed: bool

    sender: "UserShortSchema"

    model_config = ConfigDict(from_attributes=True)


PrivateMessageDataSchema.model_rebuild()
RoomDataSchema.model_rebuild()
