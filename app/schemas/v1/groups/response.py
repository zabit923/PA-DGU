from typing import Any, Dict, List, Optional

from app.schemas.v1.base import BaseResponseSchema, BaseSchema
from app.schemas.v1.users.response import UserShortSchema


class GroupResponseSchema(BaseSchema):
    methodist_id: int
    course: int
    facult: str
    subgroup: Optional[int] = None
    methodist: "UserShortSchema"
    members: List["UserShortSchema"]


class GroupShortResponseSchema(BaseSchema):
    course: int
    facult: str
    subgroup: Optional[int] = None


class GroupListResponseSchema(BaseResponseSchema):
    message: str = "Список групп успешно получен"
    data: Dict[str, Any]


GroupResponseSchema.model_rebuild()
