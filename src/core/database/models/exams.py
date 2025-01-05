from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    BOOLEAN,
    TIMESTAMP,
    Column,
    ForeignKey,
    String,
    Table,
    false,
    func,
)
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models import Base, TableNameMixin

if TYPE_CHECKING:
    from core.database.models import Group, User


class Exam(TableNameMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(VARCHAR(255))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    quantity_questions: Mapped[Optional[int]] = mapped_column(INTEGER, nullable=True)
    time: Mapped[int] = mapped_column(INTEGER)
    is_ended: Mapped[bool] = mapped_column(
        BOOLEAN, server_default=false(), default=False
    )
    is_started: Mapped[bool] = mapped_column(
        BOOLEAN, server_default=false(), default=False
    )
    start_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    end_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    created_at: Mapped[func.now()] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )

    author: Mapped["User"] = relationship(
        "User", back_populates="exams", lazy="selectin"
    )
    groups: Mapped[List["Group"]] = relationship(
        "Group",
        secondary="group_exams",
        back_populates="exams",
        lazy="joined",
    )
    questions: Mapped[List["Question"]] = relationship(
        "Question", back_populates="exam", lazy="joined", cascade="all, delete"
    )
    results: Mapped[List["ExamResult"]] = relationship(
        "ExamResult", back_populates="exam", lazy="selectin", cascade="all, delete"
    )

    def __repr__(self):
        return f"{self.title} | {self.author.username}"


class Question(TableNameMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"))
    text: Mapped[str] = mapped_column(String)
    order: Mapped[int] = mapped_column(INTEGER, nullable=True)

    exam: Mapped["Exam"] = relationship(
        "Exam",
        back_populates="questions",
        lazy="selectin",
    )
    answers: Mapped[List["Answer"]] = relationship(
        "Answer", back_populates="question", lazy="joined", cascade="all, delete"
    )

    def __repr__(self):
        return f"{self.text}"


class Answer(TableNameMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    text: Mapped[str] = mapped_column(String)
    is_correct: Mapped[bool] = mapped_column(BOOLEAN)

    question: Mapped["Question"] = relationship(
        "Question",
        back_populates="answers",
        lazy="selectin",
    )

    def __repr__(self):
        return f"{self.text}"


class ExamResult(TableNameMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"))
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    score: Mapped[int] = mapped_column(INTEGER)
    created_at: Mapped[func.now()] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )

    exam: Mapped["Exam"] = relationship(
        "Exam",
        back_populates="results",
        lazy="selectin",
    )
    student: Mapped["User"] = relationship(
        "User",
        back_populates="results",
        lazy="selectin",
    )

    def __repr__(self):
        return f"{self.exam.title} | {self.student.username} | {self.score}"


group_exams = Table(
    "group_exams",
    Base.metadata,
    Column("group_id", ForeignKey("groups.id"), primary_key=True),
    Column("exam_id", ForeignKey("exams.id"), primary_key=True),
)
