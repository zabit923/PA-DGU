from typing import Any, Dict

from app.schemas import BaseResponseSchema, BaseSchema


class CategoryResponseSchema(BaseSchema):
    title: str


class CategoryListResponseSchema(BaseResponseSchema):
    message: str = "Список категорий успешно получен"
    data: Dict[str, Any]
