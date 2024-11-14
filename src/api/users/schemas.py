from datetime import datetime

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str


class UserCreate(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
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
    is_teacher: bool
    created_at: datetime


class UserUpdate(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    is_teacher: bool
