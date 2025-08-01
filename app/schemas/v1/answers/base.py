from pydantic import Field

from app.schemas import BaseSchema


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
