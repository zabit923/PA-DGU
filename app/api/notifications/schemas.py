from datetime import datetime

from pydantic import BaseModel


class NotificationRead(BaseModel):
    id: int
    title: str
    body: str
    user: "UserShort"
    is_read: bool
    created_at: datetime


from api.users.schemas import UserShort

NotificationRead.model_rebuild()
