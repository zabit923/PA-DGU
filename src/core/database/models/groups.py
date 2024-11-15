from typing import List, Optional

from sqlalchemy import INTEGER, TIMESTAMP, VARCHAR, Column, ForeignKey, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models import Base, TableNameMixin, User


class Group(TableNameMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    curator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    course: Mapped[int] = mapped_column(INTEGER)
    facult: Mapped[str] = mapped_column(VARCHAR(50))
    subgroup: Mapped[Optional[int]] = mapped_column(INTEGER)
    created_at: Mapped[func.now()] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )

    curator: Mapped["User"] = relationship("User", back_populates="groups")
    members: Mapped[List["User"]] = relationship(
        "User", secondary="group_members", back_populates="member_groups"
    )

    def __repr__(self):
        return f"<Group {self.course}-{self.facult}-{self.subgroup}>"


group_members = Table(
    "group_members",
    Base.metadata,
    Column("group_id", ForeignKey("groups.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)
