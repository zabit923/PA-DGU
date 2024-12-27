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


class QuestionCreate(BaseModel):
    text: str
    answers: List["AnswerCreate"]


class AnswerCreate(BaseModel):
    text: str
    is_correct: bool
