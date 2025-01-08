from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from config import settings


class LectureCreate(BaseModel):
    title: str
    groups: List[int]


class LectureUpdate(BaseModel):
    title: Optional[str] = None
    groups: Optional[List[int]] = None


class LectureRead(BaseModel):
    id: int
    title: str
    author: "UserShort"
    groups: List["GroupShort"]
    file: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("file", mode="before")
    def create_image_url(cls, value: object) -> str:
        return f"http://{settings.run.host}:{settings.run.port}/static/media/{value}"


from api.groups.schemas import GroupShort
from api.users.schemas import UserShort

LectureRead.model_rebuild()
