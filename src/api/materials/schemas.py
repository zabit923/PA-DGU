from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

import config
from config import settings


class LectureCreate(BaseModel):
    title: str
    text: Optional[str] = None
    groups: List[int]


class LectureUpdate(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None
    groups: Optional[List[int]] = None


class LectureRead(BaseModel):
    id: int
    title: str
    text: Optional[str] = None
    author: "UserShort"
    groups: List["GroupShort"]
    file: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("file", mode="before")
    def create_image_url(cls, value: Optional[object]) -> Optional[str]:
        if config.DEBUG:
            return (
                f"http://{settings.run.host}:{settings.run.port}/static/media/{value}"
            )
        return f"{settings.url}/static/media/{value}"


from api.groups.schemas import GroupShort
from api.users.schemas import UserShort

LectureRead.model_rebuild()
