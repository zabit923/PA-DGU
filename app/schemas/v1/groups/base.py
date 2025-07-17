from typing import List, Optional

from pydantic import ConfigDict, Field

from app.schemas.v1.base import BaseSchema
from app.schemas.v1.users import UserShortSchema


class GroupDataSchema(BaseSchema):
    methodist_id: int = Field(
        description="ID методиста, ответственного за группу.",
    )
    course: int = Field(
        description="Курс группы.",
        ge=1,
        le=6,
    )
    facult: str = Field(
        description="Факультет группы.",
        max_length=100,
    )
    subgroup: Optional[int] = Field(
        default=None,
        description="Подгруппа группы (необязательное поле).",
        ge=1,
        le=10,
    )
    invite_token: Optional[str] = Field(
        default=None,
        description="Токен приглашения для присоединения к группе (необязательное поле).",
        max_length=128,
    )
    methodist: "UserShortSchema"
    members: List["UserShortSchema"]

    model_config = ConfigDict(from_attributes=True)


GroupDataSchema.model_rebuild()
