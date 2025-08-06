from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BOOLEAN, TIMESTAMP, Column, ForeignKey, String, Table, false
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import BaseModel

if TYPE_CHECKING:
    from app.models import Group, User


class Exam(BaseModel):
    __tablename__ = "exams"

    title: Mapped[str] = mapped_column(VARCHAR(255))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    quantity_questions: Mapped[Optional[int]] = mapped_column(INTEGER, nullable=True)
    time: Mapped[int] = mapped_column(INTEGER)
    is_advanced_exam: Mapped[bool] = mapped_column(
        BOOLEAN, server_default=false(), default=False, nullable=True
    )
    is_ended: Mapped[bool] = mapped_column(
        BOOLEAN, server_default=false(), default=False
    )
    is_started: Mapped[bool] = mapped_column(
        BOOLEAN, server_default=false(), default=False
    )
    start_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    end_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))

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
    text_questions: Mapped[List["TextQuestion"]] = relationship(
        "TextQuestion", back_populates="exam", lazy="joined", cascade="all, delete"
    )

    results: Mapped[List["ExamResult"]] = relationship(
        "ExamResult", back_populates="exam", lazy="selectin", cascade="all, delete"
    )
    passed_choice_answers: Mapped[List["PassedChoiceAnswer"]] = relationship(
        "PassedChoiceAnswer",
        back_populates="exam",
        lazy="selectin",
        cascade="all, delete",
    )
    passed_text_answers: Mapped[List["PassedTextAnswer"]] = relationship(
        "PassedTextAnswer",
        back_populates="exam",
        lazy="selectin",
        cascade="all, delete",
    )


class Question(BaseModel):
    __tablename__ = "questions"

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


class TextQuestion(BaseModel):
    __tablename__ = "text_questions"

    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"))
    text: Mapped[str] = mapped_column(String)
    order: Mapped[int] = mapped_column(INTEGER, nullable=True)

    exam: Mapped["Exam"] = relationship(
        "Exam", back_populates="text_questions", lazy="selectin"
    )


class Answer(BaseModel):
    __tablename__ = "answers"

    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    text: Mapped[str] = mapped_column(String)
    is_correct: Mapped[bool] = mapped_column(BOOLEAN)

    question: Mapped["Question"] = relationship(
        "Question",
        back_populates="answers",
        lazy="selectin",
    )


class ExamResult(BaseModel):
    __tablename__ = "exam_results"

    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"))
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    score: Mapped[Optional[int]] = mapped_column(INTEGER, nullable=True)

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


class PassedChoiceAnswer(BaseModel):
    __tablename__ = "passed_choice_answers"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"))
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE")
    )
    selected_answer_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("answers.id"), nullable=True
    )
    is_correct: Mapped[Optional[bool]] = mapped_column(BOOLEAN, nullable=True)

    user: Mapped["User"] = relationship(
        "User", back_populates="passed_choice_answers", lazy="selectin"
    )
    exam: Mapped["Exam"] = relationship(
        "Exam", back_populates="passed_choice_answers", lazy="selectin"
    )
    question: Mapped["Question"] = relationship("Question", lazy="selectin")
    selected_answer: Mapped[Optional["Answer"]] = relationship(
        "Answer", lazy="selectin"
    )


class PassedTextAnswer(BaseModel):
    __tablename__ = "passed_text_answers"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"))
    question_id: Mapped[int] = mapped_column(
        ForeignKey("text_questions.id", ondelete="CASCADE")
    )
    text: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    user: Mapped["User"] = relationship(
        "User", back_populates="passed_text_answers", lazy="selectin"
    )
    exam: Mapped["Exam"] = relationship(
        "Exam", back_populates="passed_text_answers", lazy="selectin"
    )
    question: Mapped["TextQuestion"] = relationship("TextQuestion", lazy="selectin")


group_exams = Table(
    "group_exams",
    BaseModel.metadata,
    Column("group_id", ForeignKey("groups.id"), primary_key=True),
    Column("exam_id", ForeignKey("exams.id"), primary_key=True),
)
