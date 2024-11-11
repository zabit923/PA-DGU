from fastapi_users import schemas
from pydantic import BaseModel


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(schemas.BaseUser[int]):
    username: str
    first_name: str
    last_name: str
    is_teacher: bool


class UserCreate(schemas.BaseUserCreate):
    username: str
    first_name: str
    last_name: str
    is_teacher: bool


class UserUpdate(schemas.BaseUserUpdate):
    username: str
    first_name: str
    last_name: str
    is_teacher: bool
