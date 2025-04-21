from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class PrivateMessageCreate(BaseModel):
    text: Optional[str]


class PrivateMessageUpdate(BaseModel):
    text: Optional[str] = None


class PrivateMessageRead(BaseModel):
    id: int
    text: str
    sender: "UserShort"
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoomRead(BaseModel):
    id: int
    members: List["UserShort"]
    last_message: Optional["PrivateMessageRead"]
    created_at: datetime


from api.users.schemas import UserShort

PrivateMessageRead.model_rebuild()
RoomRead.model_rebuild()
