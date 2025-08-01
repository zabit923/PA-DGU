from typing import TYPE_CHECKING, List

from pydantic import Field

from app.schemas import BaseSchema

if TYPE_CHECKING:
    from app.schemas import AnswerResponseSchema


class QuestionDataSchema(BaseSchema):
    """
    Схема данных вопроса экзамена.
    """

    exam_id: int = Field(
        description="ID экзамена, к которому относится вопрос.",
    )
    text: str = Field(
        description="Текст вопроса.",
    )
    order: int = Field(
        description="Порядок вопроса в экзамене.",
        ge=0,
    )

    answers: List["AnswerResponseSchema"] = Field(
        description="Список ответов на вопрос.",
    )


class TextQuestionDataSchema(BaseSchema):
    """
    Схема данных текстового вопроса экзамена.
    """

    exam_id: int = Field(
        description="ID экзамена, к которому относится текстовый вопрос.",
    )
    text: str = Field(
        description="Текст текстового вопроса.",
    )
    order: int = Field(
        description="Порядок текстового вопроса в экзамене.",
        ge=0,
    )
