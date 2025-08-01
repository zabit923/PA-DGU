from typing import TYPE_CHECKING, List

from pydantic import ConfigDict

from app.schemas import BaseSchema

if TYPE_CHECKING:
    from app.schemas import AnswerReadSchema, AnswerStudentResponseSchema


class QuestionResponseSchema(BaseSchema):
    """
    респонс схема вопроса экзамена.
    (Используется для получения экзамена преподавателем, т.к. содержит ответы на вопросы)
    """

    text: str
    order: int
    answers: List["AnswerReadSchema"]

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
