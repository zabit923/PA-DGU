from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BOOLEAN, VARCHAR, String, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import BaseModel

if TYPE_CHECKING:
    from app.models import (
        Exam,
        ExamResult,
        Group,
        GroupMessage,
        GroupMessageCheck,
        Lecture,
        Notification,
        PassedChoiceAnswer,
        PassedTextAnswer,
        PrivateMessage,
        PrivateRoom,
    )


class User(BaseModel):
    __tablename__ = "users"

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
    is_verified: Mapped[bool] = mapped_column(BOOLEAN, server_default=false())
    ignore_messages: Mapped[bool] = mapped_column(BOOLEAN, server_default=false())

    created_groups: Mapped[List["Group"]] = relationship(
        "Group",
        back_populates="methodist",
        lazy="selectin",
    )
    lectures: Mapped[List["Lecture"]] = relationship(
        "Lecture",
        back_populates="author",
        lazy="selectin",
        cascade="all, delete",
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
        cascade="all, delete",
    )
    sent_personal_messages: Mapped[List["PrivateMessage"]] = relationship(
        "PrivateMessage",
        back_populates="sender",
        lazy="selectin",
        cascade="all, delete",
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
        cascade="all, delete",
    )
    results: Mapped[List["ExamResult"]] = relationship(
        "ExamResult",
        back_populates="student",
        lazy="selectin",
        cascade="all, delete",
    )
    passed_choice_answers: Mapped[List["PassedChoiceAnswer"]] = relationship(
        "PassedChoiceAnswer",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete",
    )
    passed_text_answers: Mapped[List["PassedTextAnswer"]] = relationship(
        "PassedTextAnswer",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete",
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="user", lazy="selectin", cascade="all, delete"
    )
    checked_messages: Mapped[List["GroupMessageCheck"]] = relationship(
        "GroupMessageCheck", back_populates="user", lazy="selectin"
    )
