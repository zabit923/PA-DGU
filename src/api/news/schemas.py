from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from config import settings


class NewsCreate(BaseModel):
    title: str
    text: str


class NewsRead(BaseModel):
    id: int
    title: str
    text: str
    created_at: datetime
    image: Optional[str]

    @field_validator("image", mode="before")
    def create_image_url(cls, value: Optional[object]) -> Optional[str]:
        return f"http://{settings.run.host}:{settings.run.port}/static/media/{value}"


class NewsUpdate(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None
