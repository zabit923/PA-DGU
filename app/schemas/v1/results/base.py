from typing import Optional

from pydantic import Field

from app.schemas import BaseSchema


class ExamResultDataSchema(BaseSchema):
    """
    Схема данных результата экзамена.
    """

    exam_id: int = Field(
        description="ID экзамена, к которому относится результат.",
    )
    student_id: int = Field(
        description="ID студента, которому принадлежит результат.",
    )
    score: Optional[int] = Field(
        default=None,
        description="Оценка, полученная студентом за экзамен. Может быть None, если оценка не выставлена.",
    )
