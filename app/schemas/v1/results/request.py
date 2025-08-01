from app.schemas import BaseRequestSchema


class ExamResultUpdateSchema(BaseRequestSchema):
    """
    Схема для обновления результата экзамена.
    """

    score: int
