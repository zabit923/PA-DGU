from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class Token(BaseModel):
    access_token: str
    refresh_token: str


class UserCreate(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    image: Optional[HttpUrl] = None
    password: str
    is_teacher: bool


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    image: Optional[HttpUrl] = None
    is_teacher: bool
    created_at: datetime
    groups: List["GroupShort"]
    member_groups: List["GroupShort"]


class UserUpdate(BaseModel):
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    is_teacher: Optional[bool]


from api.groups.schemas import GroupShort

UserRead.update_forward_refs()
