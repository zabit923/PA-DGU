from typing import Optional

from app.schemas import BaseRequestSchema, CommonBaseSchema


class AnswerCreateSchema(BaseRequestSchema):
    """
    Схема для создания ответа на вопрос экзамена.
    """

    text: str = None
    is_correct: bool = None


class AnswerUpdateSchema(CommonBaseSchema):
    """
    Схема для обновления ответа на вопрос экзамена.
    """

    text: Optional[str] = None
    is_correct: Optional[bool] = None


class SelectAnswerDataCreateSchema(BaseRequestSchema):
    """
    Схема для создания ответа на вопрос во время прохождения экзамена.
    """

    question_id: int
    answer_id: int


class TextAnswerDataCreateSchema(BaseRequestSchema):
    """
    Схема для создания текстового ответа на вопрос во время прохождения экзамена.
    """

    question_id: int
    text: str
