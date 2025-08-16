from typing import Any, Dict, Optional

from app.schemas.v1.base import BaseResponseSchema, BaseSchema
from app.schemas.v1.categories.response import CategoryResponseSchema


class NewsResponseSchema(BaseSchema):
    title: str
    text: str
    image: Optional[str] = None
    time_to_read: int
    category: Optional["CategoryResponseSchema"] = None


class NewsListResponseSchema(BaseResponseSchema):
    message: str = "Список новостей успешно получен"
    data: Dict[str, Any]
