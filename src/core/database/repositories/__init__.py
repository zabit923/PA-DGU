from .answers import AnswerRepository
from .exams import ExamRepository
from .groups import GroupRepository
from .materials import MaterialRepository
from .notifications import NotificationRepository
from .questions import QuestionRepository
from .results import ResultRepository
from .users import UserRepository

__all__ = (
    "UserRepository",
    "NotificationRepository",
    "GroupRepository",
    "ExamRepository",
    "QuestionRepository",
    "AnswerRepository",
    "ResultRepository",
    "MaterialRepository",
)
