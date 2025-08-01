from typing import TYPE_CHECKING

from app.schemas import BaseSchema

if TYPE_CHECKING:
    from app.schemas import QuestionShortResponseSchema


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
