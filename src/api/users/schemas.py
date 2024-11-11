from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


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


class UserUpdate(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    is_teacher: bool
