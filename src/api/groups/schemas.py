from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class GroupCreate(BaseModel):
    curator_id: int
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
    curator: "UserRead"
    members: List["UserRead"]


class GroupShort(BaseModel):
    id: int
    course: int
    facult: str
    subgroup: Optional[int]


class GroupUpdate(BaseModel):
    course: Optional[int]
    facult: Optional[str]
    subgroup: Optional[int]
    members: Optional[List[int]]


from api.users.schemas import UserRead

GroupRead.update_forward_refs()