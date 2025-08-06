from typing import Any, Optional

from core.exceptions import BaseAPIException


class ExamNotFoundError(BaseAPIException):
    def __init__(
        self,
        field: Optional[str] = None,
        value: Any = None,
        detail: Optional[str] = None,
    ):
        message = detail or "Экзамен не найден"
        if field and value is not None:
            message = f"Экзамен с {field}={value} не найден"

        super().__init__(
            status_code=404,
            detail=message,
            error_type="exam_not_found",
            extra={"field": field, "value": value} if field else None,
        )


class QuestionNotFoundError(BaseAPIException):
    def __init__(
        self,
        field: Optional[str] = None,
        value: Any = None,
        detail: Optional[str] = None,
    ):
        message = detail or "Вопрос не найден"
        if field and value is not None:
            message = f"Вопрос с {field}={value} не найден"

        super().__init__(
            status_code=404,
            detail=message,
            error_type="question_not_found",
            extra={"field": field, "value": value} if field else None,
        )


class AnswerNotFoundError(BaseAPIException):
    def __init__(
        self,
        field: Optional[str] = None,
        value: Any = None,
        detail: Optional[str] = None,
    ):
        message = detail or "Ответ не найден"
        if field and value is not None:
            message = f"Ответ с {field}={value} не найден"

        super().__init__(
            status_code=404,
            detail=message,
            error_type="answer_not_found",
            extra={"field": field, "value": value} if field else None,
        )
