from typing import Optional

from app.schemas.v1.base import BaseRequestSchema, CommonBaseSchema


class GroupCreateSchema(BaseRequestSchema):
    course: int
    facult: str
    subgroup: Optional[int] = None


class GroupUpdateSchema(CommonBaseSchema):
    course: Optional[int] = None
    facult: Optional[str] = None
    subgroup: Optional[int] = None
