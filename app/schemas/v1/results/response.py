from typing import TYPE_CHECKING, Any, Dict, Optional

from app.schemas import BaseResponseSchema

from app.schemas import BaseSchema

if TYPE_CHECKING:
    from app.schemas import UserShortSchema
else:
    from app.schemas.v1.users import UserShortSchema


class ExamResultResponseSchema(BaseSchema):
    """
    Схема ответа для результатов экзамена.
    """

    exam_id: int
    student: "UserShortSchema"
    score: Optional[int] = None


class ExamResultListResponseSchema(BaseResponseSchema):
    message: str = "Список результатов экзамена получен"
    data: Dict[str, Any]


ExamResultResponseSchema.model_rebuild()
