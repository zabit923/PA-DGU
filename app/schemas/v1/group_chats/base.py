from typing import List, Optional

from pydantic import ConfigDict, Field

from app.schemas.v1.base import BaseSchema
from app.schemas.v1.groups import GroupShortResponseSchema
from app.schemas.v1.users import UserShortSchema
from .response import GroupMessageCheckResponseSchema


class GroupMessageDataSchema(BaseSchema):
    group_id: int = Field(
        description="ID группы",
    )
    sender_id: int = Field(
        description="ID отправителя сообщения.",
    )
    text: str = Field(
        description="Текст сообщения.",
    )

    group: "GroupShortResponseSchema"
    sender: "UserShortSchema"
    users_who_checked: Optional[List["GroupMessageCheckResponseSchema"]] = []

    model_config = ConfigDict(from_attributes=True)


GroupMessageDataSchema.model_rebuild()
