from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PrivateMessageCreate(BaseModel):
    text: Optional[str]


class PrivateMessageRead(BaseModel):
    id: int
    text: str
    sender: "UserShort"
    created_at: datetime

    class Config:
        from_attributes = True


from api.users.schemas import UserShort

PrivateMessageRead.update_forward_refs()
