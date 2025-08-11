from typing import List, Optional

from app.schemas.v1.base import BaseRequestSchema


class LectureCreateSchema(BaseRequestSchema):
    title: str
    text: Optional[str] = None
    groups: List[int]


class LectureUpdateSchema(BaseRequestSchema):
    title: Optional[str] = None
    text: Optional[str] = None
    groups: Optional[List[int]] = None
