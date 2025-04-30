from .exams import (
    AnswerAdmin,
    ChoiseQuestionAdmin,
    ExamAdmin,
    ResultAdmin,
    TextQuestionAdmin,
)
from .group_messages import GroupMessageAdmin
from .groups import GroupAdmin
from .lecture import LectureAdmin
from .notifications import NotificationAdmin
from .personal_messages import PersonalMessageAdmin
from .rooms import RoomAdmin
from .users import UserAdmin

__all_ = (
    "AnswerAdmin",
    "ChoiseQuestionAdmin",
    "ExamAdmin",
    "ResultAdmin",
    "TextQuestionAdmin",
    "GroupMessageAdmin",
    "GroupAdmin",
    "LectureAdmin",
    "NotificationAdmin",
    "PersonalMessageAdmin",
    "RoomAdmin",
    "UserAdmin",
)
