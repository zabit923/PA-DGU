from typing import TYPE_CHECKING, Any, Dict, List, Optional

from app.schemas.v1.base import BaseResponseSchema, BaseSchema

if TYPE_CHECKING:
    from app.schemas import GroupShortResponseSchema, UserShortSchema
else:
    from app.schemas.v1.groups import GroupShortResponseSchema
    from app.schemas.v1.users import UserShortSchema


class LectureResponseSchema(BaseSchema):
    title: str
    text: Optional[str] = None
    author: "UserShortSchema"
    groups: List["GroupShortResponseSchema"]
    file: Optional[str] = None


class LectureListResponseSchema(BaseResponseSchema):
    message: str = "Список лекций успешно получен"
    data: Dict[str, Any]


LectureResponseSchema.model_rebuild()
