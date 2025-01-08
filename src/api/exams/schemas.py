from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator


class ExamCreate(BaseModel):
    title: str
    time: int
    start_time: datetime
    end_time: datetime
    groups: List[int]
    questions: List["QuestionCreate"]

    model_config = ConfigDict(from_attributes=True)


class QuestionCreate(BaseModel):
    text: str
    order: int
    answers: List["AnswerCreate"]

    model_config = ConfigDict(from_attributes=True)


class AnswerCreate(BaseModel):
    text: str
    is_correct: bool


class ExamUpdate(BaseModel):
    title: Optional[str] = None
    time: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    groups: Optional[List[int]] = None
    questions: Optional[List["QuestionUpdate"]] = None

    model_config = ConfigDict(from_attributes=True)


class QuestionUpdate(BaseModel):
    id: Optional[int] = None
    text: Optional[str] = None
    order: Optional[int] = None
    answers: Optional[List["AnswerUpdate"]] = None

    model_config = ConfigDict(from_attributes=True)


class AnswerUpdate(BaseModel):
    id: Optional[int] = None
    text: Optional[str] = None
    is_correct: Optional[bool] = None


class ExamRead(BaseModel):
    id: int
    title: str
    author: "UserShort"
    quantity_questions: int
    time: int
    start_time: datetime
    end_time: datetime
    is_ended: bool
    is_started: bool
    groups: List["GroupShort"]
    questions: List["QuestionRead"]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("questions", mode="before")
    def sort_questions(cls, questions):
        return sorted(questions, key=lambda q: q.order)


class QuestionRead(BaseModel):
    id: int
    text: str
    order: int
    answers: List["AnswerRead"]

    model_config = ConfigDict(from_attributes=True)


class AnswerRead(BaseModel):
    id: int
    text: str
    is_correct: bool


class ExamShort(BaseModel):
    id: int
    title: str
    author: "UserShort"
    quantity_questions: int
    time: int
    start_time: datetime
    end_time: datetime
    is_ended: bool
    is_started: bool
    groups: List["GroupShort"]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


from api.groups.schemas import GroupShort
from api.users.schemas import UserShort

ExamRead.model_rebuild()
ExamShort.model_rebuild()
