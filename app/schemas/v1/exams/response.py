from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import ConfigDict

from app.schemas.v1.base import BaseSchema

if TYPE_CHECKING:
    from app.schemas import GroupShortResponseSchema, UserShortSchema
else:
    from app.schemas.v1.groups.response import GroupShortResponseSchema
    from app.schemas.v1.users.response import UserShortSchema


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


class QuestionResponseSchema(BaseSchema):
    """
    респонс схема вопроса экзамена.
    (Используется для получения экзамена преподавателем, т.к. содержит ответы на вопросы)
    """

    text: str
    order: int
    answers: List["AnswerResponseSchema"]

    model_config = ConfigDict(from_attributes=True)


class TextQuestionResponseSchema(BaseSchema):
    """
    Респонс схема текстового вопроса экзамена.
    (Не нужна версия для студента, т.к. текстовые вопросы не имеют ответов, у каждого студента ответ индивидуален)
    """

    text: str
    order: int

    model_config = ConfigDict(from_attributes=True)


class QuestionShortResponseSchema(BaseSchema):
    """
    Укороченная респонс схема вопроса экзамена.
    (Используется для получения экзамена преподавателем, т.к. содержит только текст вопроса и порядок)
    """

    text: str
    order: int


class QuestionStudentResponseSchema(BaseSchema):
    """
    Респонс схема вопроса экзамена для студента.
    (Используется для получения экзамена студентом во время экзамена, т.к. содержит только текст вопроса,
     порядок и ответы без флага is_correct)
    """

    text: str
    order: int
    answers: List["AnswerStudentResponseSchema"]

    model_config = ConfigDict(from_attributes=True)


class AnswerResponseSchema(BaseSchema):
    """
    Схема для ответа на вопрос экзамена.
    """

    text: str
    is_correct: bool


class AnswerStudentResponseSchema(BaseSchema):
    """
    Схема для ответа студента на вопрос экзамена.
    """

    text: str


class PassedChoiceAnswerResponseSchema(BaseSchema):
    """
    Схема для просмотра преподавателем на какие вопросы и как ответил студент.
    """

    question: "QuestionShortResponseSchema"
    selected_answer: "AnswerResponseSchema"
    is_correct: bool


class PassedTextAnswerResponseSchema(BaseSchema):
    """
    Схема для просмотра преподавателем на какие текстовые вопросы и как ответил студент.
    """

    question: "QuestionShortResponseSchema"
    text: str


ExamResponseSchema.model_rebuild()
ExamStudentResponseSchema.model_rebuild()
ExamShortResponseSchema.model_rebuild()
QuestionResponseSchema.model_rebuild()
QuestionStudentResponseSchema.model_rebuild()
PassedChoiceAnswerResponseSchema.model_rebuild()
PassedTextAnswerResponseSchema.model_rebuild()
