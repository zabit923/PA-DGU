from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import TEXT, TIMESTAMP, VARCHAR, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models import Base, TableNameMixin

if TYPE_CHECKING:
    from .categories import Category


class News(TableNameMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    text: Mapped[str] = mapped_column(TEXT, nullable=False)
    time_to_read: Mapped[int] = mapped_column(Integer, nullable=True, default=3)
    image: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )

    category: Mapped[Optional["Category"]] = relationship(
        "Category",
        back_populates="newses",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"{self.title} | {self.created_at}"
