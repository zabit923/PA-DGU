from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ExamCreate(BaseModel):
    course: int
    facult: str
    subgroup: Optional[int]


class GroupRead(BaseModel):
    id: int
    curator_id: int
    course: int
    facult: str
    subgroup: Optional[int]
    created_at: datetime
    curator: "UserShort"
    members: List["UserShort"]

    class Config:
        from_attributes = True


class GroupShort(BaseModel):
    id: int
    course: int
    facult: str
    subgroup: Optional[int]


class GroupUpdate(BaseModel):
    course: Optional[int] = None
    facult: Optional[str] = None
    subgroup: Optional[int] = None


class UserKickList(BaseModel):
    users_list: List[int]


from api.users.schemas import UserShort

GroupRead.update_forward_refs()
