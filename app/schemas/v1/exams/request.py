from datetime import datetime
from typing import List, Optional

from pydantic import ConfigDict

from app.schemas.v1.base import BaseRequestSchema, CommonBaseSchema


class ExamCreateSchema(BaseRequestSchema):
    """
    Схема для создания экзамена.
    """

    title: str
    time: int
    start_time: datetime
    end_time: datetime
    groups: List[int]
    questions: Optional[List["QuestionCreateSchema"]] = None
    text_questions: Optional[List["TextQuestionCreateSchema"]] = None

    model_config = ConfigDict(from_attributes=True)


class ExamUpdateSchema(CommonBaseSchema):
    """
    Схема для обновления экзамена.
    """

    title: Optional[str] = None
    time: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    groups: Optional[List[int]] = None
    questions: Optional[List["QuestionUpdateSchema"]] = None
    text_questions: Optional[List["TextQuestionUpdateSchema"]] = None

    model_config = ConfigDict(from_attributes=True)


class PassingExamDataCreateSchema(BaseRequestSchema):
    """
    Схема для создания данных о прохождении экзамена.
    """

    choise_questions: Optional[List["SelectAnswerDataCreateSchema"]] = None
    text_questions: Optional[List["TextAnswerDataCreateSchema"]] = None


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

    id: Optional[int] = None
    text: Optional[str] = None
    order: Optional[int] = None
    answers: Optional[List["AnswerUpdateSchema"]] = None

    model_config = ConfigDict(from_attributes=True)


class TextQuestionUpdateSchema(CommonBaseSchema):
    """
    Схема для обновления текстового вопроса экзамена.
    """

    id: Optional[int] = None
    text: Optional[str] = None
    order: Optional[int] = None


ExamUpdateSchema.model_rebuild()
PassingExamDataCreateSchema.model_rebuild()
ExamCreateSchema.model_rebuild()
QuestionCreateSchema.model_rebuild()
QuestionUpdateSchema.model_rebuild()
