from typing import List

from pydantic import Field

from app.schemas.v1.base import BaseSchema
from app.schemas.v1.groups import GroupShortResponseSchema
from app.schemas.v1.users import UserShortSchema


class LectureDataSchema(BaseSchema):
    title: str = Field(
        description="Название лекции",
        example="Введение в программирование",
    )
    body: str = Field(
        description="Текст лекции",
        example="В этой лекции мы рассмотрим основы программирования.",
    )
    author: "UserShortSchema"
    groups: List["GroupShortResponseSchema"]
