from datetime import datetime
from typing import List

from pydantic import BaseModel


class ExamCreate(BaseModel):
    title: str
    quantity_questions: int
    time: int
    start_time: datetime
    end_time: datetime
    groups: List[int]
    questions: List["QuestionCreate"]

    class Config:
        from_attributes = True


class QuestionCreate(BaseModel):
    text: str
    answers: List["AnswerCreate"]

    class Config:
        from_attributes = True


class AnswerCreate(BaseModel):
    text: str
    is_correct: bool


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


class QuestionRead(BaseModel):
    id: int
    text: str
    answers: List["AnswerRead"]

    class Config:
        from_attributes = True


class AnswerRead(BaseModel):
    id: int
    text: str
    is_correct: bool


from api.groups.schemas import GroupShort

ExamRead.update_forward_refs()
