from .answers import AnswerRepository
from .categories import CategoryRepository
from .exams import ExamRepository
from .group_messages import GroupMessageRepository
from .groups import GroupRepository
from .materials import MaterialRepository
from .news import NewsRepository
from .notifications import NotificationRepository
from .private_messages import PrivateMessageRepository
from .questions import QuestionRepository
from .results import ResultRepository
from .rooms import RoomRepository
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
    "RoomRepository",
    "PrivateMessageRepository",
    "GroupMessageRepository",
    "NewsRepository",
    "CategoryRepository",
)
