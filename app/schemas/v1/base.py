from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class CommonBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    def to_dict(self) -> dict:
        return self.model_dump()


class BaseSchema(CommonBaseSchema):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserBaseSchema(CommonBaseSchema):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BaseRequestSchema(CommonBaseSchema):
    """
    Базовая схема для входных данных.
    Этот класс наследуется от `CommonBaseSchema`
    и предоставляет общую конфигурацию для всех схем входных данных.

    Так как нету необходимости для ввода исходных данных id и даты создания и обновления.
    """


class BaseCommonResponseSchema(CommonBaseSchema):
    """
    Базовая схема для ответов API (без success и message).

    Этот класс наследуется от `CommonBaseSchema` и предоставляет общую
    конфигурацию для всех схем ответов.
    """


class BaseResponseSchema(CommonBaseSchema):
    success: bool = True
    message: Optional[str] = None


class ErrorSchema(CommonBaseSchema):
    detail: str
    error_type: str
    status_code: int
    timestamp: str
    request_id: str
    extra: Optional[Dict[str, Any]] = None


class ErrorResponseSchema(BaseResponseSchema):
    success: bool = False
    message: Optional[str] = None
    data: None = None
    error: ErrorSchema


class ItemResponseSchema(BaseResponseSchema, Generic[T]):
    item: T


class ListResponseSchema(BaseResponseSchema, Generic[T]):
    items: List[T]


class MetaResponseSchema(BaseResponseSchema):
    meta: dict
