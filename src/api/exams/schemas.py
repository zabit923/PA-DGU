from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator


class ExamCreate(BaseModel):
    title: str
    time: int
    start_time: datetime
    end_time: datetime
    groups: List[int]
    questions: List["QuestionCreate"]

    class Config:
        from_attributes = True


class QuestionCreate(BaseModel):
    text: str
    order: int
    answers: List["AnswerCreate"]

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


class QuestionUpdate(BaseModel):
    id: Optional[int] = None
    text: Optional[str] = None
    order: Optional[int] = None
    answers: Optional[List["AnswerUpdate"]] = None

    class Config:
        from_attributes = True


class AnswerUpdate(BaseModel):
    id: Optional[int] = None
    text: Optional[str] = None
    is_correct: Optional[bool] = None


class ExamRead(BaseModel):
    id: int
    title: str
    quantity_questions: int
    time: int
    start_time: datetime
    end_time: datetime
    groups: List["GroupShort"]
    questions: List["QuestionRead"]

    class Config:
        from_attributes = True

    @field_validator("questions", mode="before")
    def sort_questions(cls, questions):
        return sorted(questions, key=lambda q: q.order)


class QuestionRead(BaseModel):
    id: int
    text: str
    order: int
    answers: List["AnswerRead"]

    class Config:
        from_attributes = True


class AnswerRead(BaseModel):
    id: int
    text: str
    is_correct: bool


class ExamShort(BaseModel):
    id: int
    title: str
    quantity_questions: int
    time: int
    start_time: datetime
    end_time: datetime
    groups: List["GroupShort"]

    class Config:
        from_attributes = True


from api.groups.schemas import GroupShort

ExamRead.update_forward_refs()
ExamShort.update_forward_refs()
