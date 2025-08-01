from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import ConfigDict

from app.schemas.v1.base import BaseResponseSchema, BaseSchema

if TYPE_CHECKING:
    from app.schemas import (
        GroupShortResponseSchema,
        QuestionResponseSchema,
        QuestionStudentResponseSchema,
        TextQuestionResponseSchema,
        UserShortSchema,
    )


class ExamResponseSchema(BaseSchema):
    """
    Схема для экзамена, возвращаемая при запросе на получение информации о конкретном экзамене.
    (Используется преподавателями и администраторами)
    """

    title: str
    author: "UserShortSchema"
    quantity_questions: int
    time: int
    is_advanced_exam: bool
    start_time: datetime
    end_time: datetime
    is_ended: bool
    is_started: bool
    groups: List["GroupShortResponseSchema"]
    questions: Optional[List["QuestionResponseSchema"]] = None
    text_questions: Optional[List["TextQuestionResponseSchema"]] = None

    model_config = ConfigDict(from_attributes=True)


class ExamStudentResponseSchema(BaseSchema):
    """
    Схема для экзамена, возвращаемая при запросе на получение информации о конкретном экзамене.
    (Используется студентами во время прохождения экзамена)
    """

    title: str
    author: "UserShortSchema"
    quantity_questions: int
    time: int
    start_time: datetime
    end_time: datetime
    is_ended: bool
    is_started: bool
    groups: List["GroupShortResponseSchema"]
    questions: Optional[List["QuestionStudentResponseSchema"]] = None
    text_questions: Optional[List["TextQuestionResponseSchema"]] = None

    model_config = ConfigDict(from_attributes=True)


class ExamShortResponseSchema(BaseSchema):
    title: str
    author: "UserShortSchema"
    quantity_questions: int
    time: int
    start_time: datetime
    end_time: datetime
    is_ended: bool
    is_started: bool
    groups: List["GroupShortResponseSchema"]


class ExamListResponseSchema(BaseResponseSchema):
    message: str = "Список групп экзаменов получен"
    data: Dict[str, Any]
