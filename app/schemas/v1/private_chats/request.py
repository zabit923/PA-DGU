from datetime import datetime
from typing import Optional

from pydantic import ConfigDict

from app.schemas.v1.base import BaseRequestSchema, BaseSchema
from app.schemas.v1.users import UserShortSchema


class PrivateMessageCreateSchema(BaseRequestSchema):
    text: Optional[str]


class PrivateMessageUpdateSchema(BaseRequestSchema):
    text: Optional[str] = None
