from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models import Base

if TYPE_CHECKING:
    from .news import News


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )

    newses: Mapped[list["News"]] = relationship(
        "News", back_populates="category", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"{self.title} | {self.created_at}"
