from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from config import settings


class NewsCreate(BaseModel):
    title: str
    text: str
    time_to_read: int = 3
    category_id: Optional[int] = None


class NewsRead(BaseModel):
    id: int
    title: str
    text: str
    time_to_read: int
    created_at: datetime
    category: Optional["CategoryRead"] = None
    image: Optional[str]

    model_config = ConfigDict(from_attributes=True)

    @field_validator("image", mode="before")
    def create_image_url(cls, value: Optional[object]) -> Optional[str]:
        if value:
            return (
                f"http://{settings.run.host}:{settings.run.port}/static/media/{value}"
            )
        return None


class NewsUpdate(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None
    category_id: Optional[int] = None
    time_to_read: Optional[int] = None


from src.api.categories.schemas import CategoryRead

NewsRead.model_rebuild()
