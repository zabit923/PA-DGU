from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class GroupMessageCreate(BaseModel):
    text: Optional[str]


class GroupMessageUpdate(BaseModel):
    text: Optional[str] = None


class GroupMessageCheckRead(BaseModel):
    id: int
    user: "UserShort"
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GroupMessageRead(BaseModel):
    id: int
    text: str
    sender: "UserShort"
    users_who_checked: List["GroupMessageCheckRead"]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


from api.users.schemas import UserShort

GroupMessageRead.model_rebuild()
GroupMessageCheckRead.model_rebuild()
