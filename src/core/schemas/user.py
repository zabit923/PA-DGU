from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    first_name: str
    last_name: str
    is_teacher: bool


class UserCreate(schemas.BaseUserCreate):
    first_name: str
    last_name: str
    is_teacher: bool


class UserUpdate(schemas.BaseUserUpdate):
    first_name: str
    last_name: str
    is_teacher: bool
