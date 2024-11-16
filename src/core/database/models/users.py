from typing import TYPE_CHECKING, List

from sqlalchemy import BOOLEAN, TIMESTAMP, VARCHAR, String, false, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models import Base, TableNameMixin, str_128

if TYPE_CHECKING:
    from core.database.models import Group


class User(TableNameMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        VARCHAR(128), unique=True, index=True, nullable=False
    )
    first_name: Mapped[str_128]
    last_name: Mapped[str_128]
    email: Mapped[str] = mapped_column(VARCHAR(255), unique=True)
    image: Mapped[str] = mapped_column(String, nullable=True)
    password: Mapped[str] = mapped_column(String)
    is_superuser: Mapped[bool] = mapped_column(BOOLEAN, server_default=false())
    is_teacher: Mapped[bool] = mapped_column(BOOLEAN, server_default=false())
    created_at: Mapped[func.now()] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )

    groups: Mapped[List["Group"]] = relationship("Group", back_populates="curator")
    member_groups: Mapped[List["Group"]] = relationship(
        "Group", secondary="group_members", back_populates="members"
    )

    def __repr__(self):
        return f"<User {self.username}>"
