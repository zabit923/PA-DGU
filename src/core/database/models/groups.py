from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import INTEGER, TIMESTAMP, VARCHAR, Column, ForeignKey, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models import Base, TableNameMixin

if TYPE_CHECKING:
    from core.database.models import User


class Group(TableNameMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    curator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    course: Mapped[int] = mapped_column(INTEGER)
    facult: Mapped[str] = mapped_column(VARCHAR(50))
    subgroup: Mapped[Optional[int]] = mapped_column(INTEGER)
    created_at: Mapped[func.now()] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )

    curator: Mapped["User"] = relationship(
        "User", back_populates="groups", lazy="selectin"
    )
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="groups", lazy="selectin"
    )
    members: Mapped[List["User"]] = relationship(
        "User",
        secondary="group_members",
        back_populates="member_groups",
        lazy="selectin",
    )

    def __repr__(self):
        return f"{self.course} курс|{self.facult}|{self.subgroup}"


class Organization(TableNameMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(VARCHAR(128), unique=True)
    created_at: Mapped[func.now()] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )

    groups: Mapped[List["Group"]] = relationship(
        "Group", back_populates="organization", lazy="selectin"
    )

    def __repr__(self):
        return f"{self.name}"


group_members = Table(
    "group_members",
    Base.metadata,
    Column("group_id", ForeignKey("groups.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)
