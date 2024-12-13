from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class GroupMessageCreate(BaseModel):
    text: Optional[str]


class GroupMessageRead(BaseModel):
    id: int
    text: str
    sender: "UserShort"
    created_at: datetime

    class Config:
        from_attributes = True


from api.users.schemas import UserShort

GroupMessageRead.update_forward_refs()
