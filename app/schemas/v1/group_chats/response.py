from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import ConfigDict

from app.schemas.v1.base import BaseResponseSchema, BaseSchema
from app.schemas.v1.users import UserShortSchema


class GroupMessageResponseSchema(BaseSchema):
    text: str
    sender: "UserShortSchema"
    users_who_checked: Optional[List["GroupMessageCheckResponseSchema"]] = []
    group_id: int

    model_config = ConfigDict(from_attributes=True)


class GroupMessageCheckResponseSchema(BaseSchema):
    user: "UserShortSchema"

    model_config = ConfigDict(from_attributes=True)


class GroupMessageListResponseSchema(BaseResponseSchema):
    message: str = "Список сообщений успешно получен"
    data: Dict[str, Any]


GroupMessageResponseSchema.model_rebuild()
GroupMessageCheckResponseSchema.model_rebuild()
