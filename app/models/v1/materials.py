from typing import TYPE_CHECKING, List

from sqlalchemy import TEXT, Column, ForeignKey, String, Table
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import BaseModel

if TYPE_CHECKING:
    from app.models import Group, User


class Lecture(BaseModel):
    __tablename__ = "lectures"

    title: Mapped[str] = mapped_column(VARCHAR(255))
    text: Mapped[str] = mapped_column(TEXT, nullable=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    file: Mapped[str] = mapped_column(String, nullable=True)

    author: Mapped["User"] = relationship(
        "User", back_populates="lectures", lazy="selectin"
    )
    groups: Mapped[List["Group"]] = relationship(
        "Group",
        secondary="group_lectures",
        back_populates="lectures",
        lazy="selectin",
    )


group_lectures = Table(
    "group_lectures",
    BaseModel.metadata,
    Column("group_id", ForeignKey("groups.id"), primary_key=True),
    Column("lecture_id", ForeignKey("lectures.id"), primary_key=True),
)
