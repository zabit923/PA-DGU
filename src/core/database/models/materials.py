from typing import TYPE_CHECKING, List

from sqlalchemy import TIMESTAMP, Column, ForeignKey, String, Table, func
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models import Base, TableNameMixin

if TYPE_CHECKING:
    from core.database.models import Group, User


class Lecture(TableNameMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(VARCHAR(255))
    author_id: Mapped[[int]] = mapped_column(ForeignKey("users.id"))
    file: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[func.now()] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )

    author: Mapped["User"] = relationship(
        "User", back_populates="lectures", lazy="selectin"
    )
    groups: Mapped[List["Group"]] = relationship(
        "Group",
        secondary="group_lectures",
        back_populates="lectures",
        lazy="selectin",
    )

    def __repr__(self):
        return f"{self.title} | {self.groups}"


group_lectures = Table(
    "group_lectures",
    Base.metadata,
    Column("group_id", ForeignKey("groups.id"), primary_key=True),
    Column("lecture_id", ForeignKey("lectures.id"), primary_key=True),
)
