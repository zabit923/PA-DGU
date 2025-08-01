from typing import TYPE_CHECKING, Any, Dict, Optional

from schemas import BaseResponseSchema

from app.schemas import BaseSchema

if TYPE_CHECKING:
    from app.schemas import UserShortSchema


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
