from typing import TYPE_CHECKING, Optional

from sqlalchemy import TEXT, VARCHAR, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import BaseModel

if TYPE_CHECKING:
    from app.models import Category


class News(BaseModel):
    __tablename__ = "news"

    title: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    text: Mapped[str] = mapped_column(TEXT, nullable=False)
    time_to_read: Mapped[int] = mapped_column(Integer, nullable=True, default=3)
    image: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )

    category: Mapped[Optional["Category"]] = relationship(
        "Category",
        back_populates="newses",
        lazy="selectin",
    )
