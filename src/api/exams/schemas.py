from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator


class ExamCreate(BaseModel):
    title: str
    time: int
    start_time: datetime
    end_time: datetime
    groups: List[int]
    questions: Optional[List["QuestionCreate"]] = None
    text_questions: Optional[List["TextQuestionCreate"]] = None

    model_config = ConfigDict(from_attributes=True)


class QuestionCreate(BaseModel):
    text: str
    order: int
    answers: List["AnswerCreate"]

    model_config = ConfigDict(from_attributes=True)


class TextQuestionCreate(BaseModel):
    text: str
    order: int


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
    text_questions: Optional[List["TextQuestionUpdate"]] = None

    model_config = ConfigDict(from_attributes=True)


class QuestionUpdate(BaseModel):
    id: Optional[int] = None
    text: Optional[str] = None
    order: Optional[int] = None
    answers: Optional[List["AnswerUpdate"]] = None

    model_config = ConfigDict(from_attributes=True)


class TextQuestionUpdate(BaseModel):
    id: Optional[int] = None
    text: Optional[str] = None
    order: Optional[int] = None


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
    is_advanced_exam: bool
    start_time: datetime
    end_time: datetime
    is_ended: bool
    is_started: bool
    groups: List["GroupShort"]
    questions: List["QuestionRead"]
    text_questions: List["TextQuestionRead"]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExamStudentRead(BaseModel):
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
    questions: List["QuestionStudentRead"]
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


class TextQuestionRead(BaseModel):
    id: int
    text: str
    order: int


class ShortQuestionRead(BaseModel):
    id: int
    text: str
    order: int


class QuestionStudentRead(BaseModel):
    id: int
    text: str
    order: int
    answers: List["AnswerStudentRead"]

    model_config = ConfigDict(from_attributes=True)


class AnswerRead(BaseModel):
    id: int
    text: str
    is_correct: bool


class AnswerStudentRead(BaseModel):
    id: int
    text: str


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


class AnswersData(BaseModel):
    question_id: int
    answer_id: int


class ResultRead(BaseModel):
    id: int
    exam_id: int
    student: "UserShort"
    score: int
    created_at: datetime


class PassedChoiceAnswerRead(BaseModel):
    id: int
    question: "ShortQuestionRead"
    selected_answer: "AnswerRead"
    is_correct: bool
    created_at: datetime


class PassedTextAnswerRead(BaseModel):
    id: int
    question: "ShortQuestionRead"
    text: str
    created_at: datetime


from api.groups.schemas import GroupShort
from api.users.schemas import UserShort

ExamRead.model_rebuild()
ExamShort.model_rebuild()
ResultRead.model_rebuild()
