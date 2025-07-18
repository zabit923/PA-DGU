import secrets
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import INTEGER, VARCHAR, Column, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import BaseModel

if TYPE_CHECKING:
    from app.models import Exam, Lecture, User


class Group(BaseModel):
    __tablename__ = "groups"

    methodist_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    course: Mapped[int] = mapped_column(INTEGER)
    facult: Mapped[str] = mapped_column(VARCHAR(50))
    subgroup: Mapped[Optional[int]] = mapped_column(INTEGER)
    invite_token: Mapped[Optional[str]] = mapped_column(
        VARCHAR(128),
        unique=True,
        nullable=True,
        default=lambda: secrets.token_urlsafe(16),
    )

    methodist: Mapped["User"] = relationship(
        "User", back_populates="created_groups", lazy="selectin"
    )
    lectures: Mapped[List["Lecture"]] = relationship(
        "Lecture",
        back_populates="groups",
        secondary="group_lectures",
        lazy="selectin",
    )
    members: Mapped[List["User"]] = relationship(
        "User",
        secondary="group_members",
        back_populates="member_groups",
        lazy="selectin",
    )
    group_messages = relationship(
        "GroupMessage", back_populates="group", lazy="selectin", cascade="all, delete"
    )
    exams: Mapped[List["Exam"]] = relationship(
        "Exam",
        secondary="group_exams",
        back_populates="groups",
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

    def generate_invite_token(self):
        self.invite_token = secrets.token_urlsafe(16)


group_members = Table(
    "group_members",
    BaseModel.metadata,
    Column("group_id", ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)
