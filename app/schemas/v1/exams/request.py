from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import ConfigDict

from app.schemas.v1.base import BaseRequestSchema, CommonBaseSchema

if TYPE_CHECKING:
    from app.schemas import (
        QuestionCreate,
        SelectedAnswerData,
        TextAnswerData,
        TextQuestionCreate,
    )


class ExamCreateSchema(BaseRequestSchema):
    """
    Схема для создания экзамена.
    """

    title: str
    time: int
    start_time: datetime
    end_time: datetime
    groups: List[int]
    questions: Optional[List["QuestionCreate"]] = None
    text_questions: Optional[List["TextQuestionCreate"]] = None

    model_config = ConfigDict(from_attributes=True)


class ExamUpdateSchema(CommonBaseSchema):
    """
    Схема для обновления экзамена.
    """

    course: Optional[int] = None
    facult: Optional[str] = None
    subgroup: Optional[int] = None


class PassingExamDataCreateSchema(BaseRequestSchema):
    """
    Схема для создания данных о прохождении экзамена.
    """

    choise_questions: Optional[List["SelectedAnswerData"]] = None
    text_questions: Optional[List["TextAnswerData"]] = None
