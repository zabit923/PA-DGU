from typing import List, Optional

from app.schemas.v1.base import BaseResponseSchema, BaseSchema
from app.schemas.v1.pagination import Page
from app.schemas.v1.users import UserShortSchema


class GroupResponseSchema(BaseSchema):
    methodist_id: int
    course: int
    facult: str
    subgroup: Optional[int] = None
    methodist: "UserShortSchema"
    members: List["UserShortSchema"]


class GroupShortResponseSchema(BaseSchema):
    id: int
    course: int
    facult: str
    subgroup: Optional[int] = None


class GroupListResponseSchema(BaseResponseSchema):
    message: str = "Список групп успешно получен"
    data: Page[GroupShortResponseSchema]


GroupResponseSchema.model_rebuild()
