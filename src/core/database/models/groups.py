import secrets
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    INTEGER,
    TIMESTAMP,
    VARCHAR,
    Column,
    ForeignKey,
    Table,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models import Base, TableNameMixin

if TYPE_CHECKING:
    from core.database.models import User


class Group(TableNameMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    curator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    course: Mapped[int] = mapped_column(INTEGER)
    facult: Mapped[str] = mapped_column(VARCHAR(50))
    subgroup: Mapped[Optional[int]] = mapped_column(INTEGER)
    invite_token: Mapped[Optional[str]] = mapped_column(
        VARCHAR(128),
        unique=True,
        nullable=True,
        default=lambda: secrets.token_urlsafe(16),
    )
    created_at: Mapped[func.now()] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )

    curator: Mapped["User"] = relationship(
        "User", back_populates="groups", lazy="selectin"
    )
    members: Mapped[List["User"]] = relationship(
        "User",
        secondary="group_members",
        back_populates="member_groups",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint(
            "facult",
            "course",
            "subgroup",
            name="uix_facult_course_subgroup",
        ),
    )

    def __repr__(self):
        return f"{self.course} курс|{self.facult}|{self.subgroup}"

    def generate_invite_token(self):
        self.invite_token = secrets.token_urlsafe(16)


group_members = Table(
    "group_members",
    Base.metadata,
    Column("group_id", ForeignKey("groups.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)
