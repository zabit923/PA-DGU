from app.models import (
    Answer,
    Category,
    Exam,
    ExamResult,
    Group,
    GroupMessage,
    Lecture,
    News,
    Notification,
    PassedChoiceAnswer,
    PassedTextAnswer,
    PrivateMessage,
    PrivateRoom,
    Question,
    TextQuestion,
    User,
)

from .config import admin
from .views.categories import CategoryAdmin
from .views.exams import (
    AnswerAdmin,
    ExamAdmin,
    ExamResultAdmin,
    PassedChoiceAnswerAdmin,
    PassedTextAnswerAdmin,
    QuestionAdmin,
    TextQuestionAdmin,
)
from .views.group_messages import GroupMessageAdmin
from .views.groups import GroupAdmin
from .views.materials import LectureAdmin
from .views.news import NewsAdmin
from .views.notifications import NotificationAdmin
from .views.personal_mesages import PersonalMessageAdmin
from .views.rooms import RoomAdmin
from .views.users import UserAdmin

admin.add_view(UserAdmin(model=User, icon="fa-solid fa-user"))
admin.add_view(GroupAdmin(model=Group, icon="fa fa-address-card"))
admin.add_view(GroupMessageAdmin(model=GroupMessage, icon="fa-solid fa-comments"))
admin.add_view(PersonalMessageAdmin(model=PrivateMessage, icon="fa-solid fa-comment"))
admin.add_view(RoomAdmin(model=PrivateRoom, icon="fa-solid fa-people-arrows"))
admin.add_view(LectureAdmin(model=Lecture, icon="fa-solid fa-book"))
admin.add_view(ExamAdmin(model=Exam, icon="fa-solid fa-pen"))
admin.add_view(QuestionAdmin(model=Question, icon="fa-solid fa-circle-question"))
admin.add_view(
    TextQuestionAdmin(model=TextQuestion, icon="fa-solid fa-circle-question")
)
admin.add_view(AnswerAdmin(model=Answer, icon="fa fa-check-circle"))
admin.add_view(
    ExamResultAdmin(model=ExamResult, icon="fa-solid fa-square-poll-vertical")
)
admin.add_view(NotificationAdmin(model=Notification, icon="fa-solid fa-envelope"))
admin.add_view(NewsAdmin(model=News, icon="fa-solid fa-newspaper"))
admin.add_view(CategoryAdmin(model=Category, icon="fa-solid fa-list"))
# admin.add_view(PassedTextAnswerAdmin(model=PassedTextAnswer))
# admin.add_view(PassedChoiceAnswerAdmin(model=PassedChoiceAnswer))
