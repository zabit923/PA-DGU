from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CategoryCreate(BaseModel):
    title: str


class CategoryUpdate(BaseModel):
    title: Optional[str] = None


class CategoryRead(BaseModel):
    id: int
    title: str
    created_at: datetime
