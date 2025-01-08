from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class GroupMessageCreate(BaseModel):
    text: Optional[str]


class GroupMessageUpdate(BaseModel):
    text: Optional[str] = None


class GroupMessageRead(BaseModel):
    id: int
    text: str
    sender: "UserShort"
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


from api.users.schemas import UserShort

GroupMessageRead.model_rebuild()
