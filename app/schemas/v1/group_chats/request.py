from datetime import datetime
from typing import Optional

from pydantic import ConfigDict

from app.schemas.v1.base import BaseRequestSchema, BaseSchema
from app.schemas.v1.users import UserShortSchema


class GroupMessageCreateSchema(BaseRequestSchema):
    text: Optional[str]


class GroupMessageUpdate(BaseRequestSchema):
    text: Optional[str] = None


class GroupMessageCheckCreateSchema(BaseSchema):
    id: int
    user: "UserShortSchema"
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
