from typing import TYPE_CHECKING, List, Optional

from pydantic import ConfigDict, Field

from app.schemas.v1.base import BaseSchema

if TYPE_CHECKING:
    from app.schemas import (
        AnswerResponseSchema,
        GroupShortResponseSchema,
        UserShortSchema,
    )
else:
    from app.schemas.v1.exams.response import AnswerResponseSchema
    from app.schemas.v1.groups import GroupShortResponseSchema
    from app.schemas.v1.users import UserShortSchema


class ExamDataSchema(BaseSchema):
    """
    Схема данных экзамена, используемая для создания и обновления экзаменов.
    """

    title: str = Field(
        description="Название экзамена.",
        max_length=255,
    )
    author_id: int = Field(
        description="ID автора экзамена.",
    )
    quantity_questions: Optional[int] = Field(
        default=None,
        description="Количество вопросов в экзамене.",
    )
    time: int = Field(
        description="Время на прохождение экзамена в минутах.",
        ge=1,
    )
    is_advanced_exam: bool = Field(
        default=False,
        description="Флаг, указывающий, есть ли в экзамене расширенные вопросы.",
    )
    is_ended: bool = Field(
        default=False,
        description="Флаг, указывающий, завершен ли экзамен.",
    )
    is_started: bool = Field(
        default=False,
        description="Флаг, указывающий, начат ли экзамен.",
    )
    start_time: str = Field(
        default=None,
        description="Время начала экзамена в формате ISO 8601.",
    )
    end_time: str = Field(
        default=None,
        description="Время окончания экзамена в формате ISO 8601.",
    )
    author: "UserShortSchema"
    groups: List["GroupShortResponseSchema"] = Field(
        description="Список групп, связанных с экзаменом.",
    )
    questions: List["QuestionDataSchema"] = Field(
        description="Список вопросов, связанных с экзаменом.",
    )
    text_questions: List["TextQuestionDataSchema"] = Field(
        description="Список текстовых вопросов, связанных с экзаменом.",
    )

    model_config = ConfigDict(from_attributes=True)


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


class AnswerDataSchema(BaseSchema):
    """
    Схема для данных ответа на вопрос экзамена.
    """

    question_id: int = Field(
        description="ID вопроса, на который дан ответ.",
    )
    text: str = Field(
        description="Текст ответа на вопрос.",
    )
    is_correct: bool = Field(
        description="Флаг, указывающий, является ли ответ правильным.",
    )


QuestionDataSchema.model_rebuild()
ExamDataSchema.model_rebuild()
