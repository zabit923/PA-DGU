from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BOOLEAN, TIMESTAMP, VARCHAR, String, false, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models import Base, TableNameMixin

if TYPE_CHECKING:
    from core.database.models import (
        Exam,
        ExamResult,
        Group,
        GroupMessage,
        Lecture,
        Notification,
        PassedAnswer,
        PrivateMessage,
        PrivateRoom,
    )


class User(TableNameMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        VARCHAR(128), unique=True, index=True, nullable=False
    )
    first_name: Mapped[str] = mapped_column(VARCHAR(128), unique=True)
    last_name: Mapped[str] = mapped_column(VARCHAR(128), unique=True)
    email: Mapped[str] = mapped_column(VARCHAR(255), unique=True)
    image: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, default="user.png"
    )
    password: Mapped[str] = mapped_column(String)
    is_online: Mapped[bool] = mapped_column(BOOLEAN, server_default=false())
    is_superuser: Mapped[bool] = mapped_column(BOOLEAN, server_default=false())
    is_teacher: Mapped[bool] = mapped_column(BOOLEAN, server_default=false())
    is_active: Mapped[bool] = mapped_column(BOOLEAN, server_default=false())
    ignore_messages: Mapped[bool] = mapped_column(BOOLEAN, server_default=false())
    created_at: Mapped[func.now()] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )

    created_groups: Mapped[List["Group"]] = relationship(
        "Group",
        back_populates="curator",
        lazy="selectin",
    )
    lectures: Mapped[List["Lecture"]] = relationship(
        "Lecture",
        back_populates="author",
        lazy="selectin",
    )
    member_groups: Mapped[List["Group"]] = relationship(
        "Group",
        secondary="group_members",
        back_populates="members",
        lazy="selectin",
    )
    sent_group_messages: Mapped[List["GroupMessage"]] = relationship(
        "GroupMessage",
        back_populates="sender",
        lazy="selectin",
    )
    sent_personal_messages: Mapped[List["PrivateMessage"]] = relationship(
        "PrivateMessage",
        back_populates="sender",
        lazy="selectin",
    )
    rooms: Mapped[List["PrivateRoom"]] = relationship(
        "PrivateRoom",
        secondary="room_members",
        back_populates="members",
        lazy="selectin",
    )
    exams: Mapped[List["Exam"]] = relationship(
        "Exam",
        back_populates="author",
        lazy="selectin",
    )
    results: Mapped[List["ExamResult"]] = relationship(
        "ExamResult",
        back_populates="student",
        lazy="selectin",
    )
    passed_answers: Mapped[List["PassedAnswer"]] = relationship(
        "PassedAnswer", back_populates="user", lazy="selectin", cascade="all, delete"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="user", lazy="selectin", cascade="all, delete"
    )

    def __repr__(self):
        return f"{self.username}"
