from typing import TYPE_CHECKING, List, Optional

from pydantic import ConfigDict

from app.schemas import BaseRequestSchema, CommonBaseSchema

if TYPE_CHECKING:
    from app.schemas import AnswerCreateSchema, AnswerUpdateSchema


class QuestionCreateSchema(BaseRequestSchema):
    """
    Схема для создания вопроса экзамена.
    """

    text: str
    order: int
    answers: List["AnswerCreateSchema"]

    model_config = ConfigDict(from_attributes=True)


class TextQuestionCreateSchema(BaseRequestSchema):
    """
    Схема для создания текстового вопроса экзамена.
    """

    text: str
    order: int


class QuestionUpdateSchema(CommonBaseSchema):
    """
    Схема для обновления вопроса экзамена.
    """

    text: Optional[str] = None
    order: Optional[int] = None
    answers: Optional[List["AnswerUpdateSchema"]] = None

    model_config = ConfigDict(from_attributes=True)


class TextQuestionUpdateSchema(CommonBaseSchema):
    """
    Схема для обновления текстового вопроса экзамена.
    """

    text: Optional[str] = None
    order: Optional[int] = None
