from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import BaseModel

if TYPE_CHECKING:
    from app.models import News


class Category(BaseModel):
    __tablename__ = "categories"

    title: Mapped[str] = mapped_column(nullable=False, unique=True)

    newses: Mapped[list["News"]] = relationship(
        "News", back_populates="category", lazy="selectin"
    )
