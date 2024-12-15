from datetime import datetime
from typing import List

from pydantic import BaseModel, field_validator

from config import settings


class LectureCreate(BaseModel):
    title: str
    groups: List[int]


class LectureRead(BaseModel):
    id: int
    title: str
    author: "UserShort"
    groups: List["GroupShort"]
    file: str
    created_at: datetime

    class Config:
        from_attributes = True

    @field_validator("file", mode="before")
    def create_image_url(cls, value: object) -> str:
        return f"http://{settings.run.host}:{settings.run.port}/static/media/{value}"


from api.groups.schemas import GroupShort
from api.users.schemas import UserShort

LectureRead.update_forward_refs()
