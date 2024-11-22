from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class GroupCreate(BaseModel):
    course: int
    facult: str
    subgroup: Optional[int]
    organization: int


class GroupRead(BaseModel):
    id: int
    curator_id: int
    course: int
    facult: str
    subgroup: Optional[int]
    organization: "OrganizationRead"
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
    course: Optional[int]
    facult: Optional[str]
    subgroup: Optional[int]
    members: Optional[List[int]]


class OrganizationRead(BaseModel):
    id: int
    name: str


from api.users.schemas import UserShort

GroupRead.update_forward_refs()
