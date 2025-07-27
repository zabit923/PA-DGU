from typing import Optional

from schemas import BaseRequestSchema


class NewsCreateSchema(BaseRequestSchema):
    title: str
    text: str
    time_to_read: int
    category_id: Optional[int] = None


class NewsUpdateSchema(BaseRequestSchema):
    title: Optional[str] = None
    text: Optional[str] = None
    time_to_read: Optional[int] = None
    category_id: Optional[int] = None
