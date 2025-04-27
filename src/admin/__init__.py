from app import admin

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

admin.add_view(UserAdmin)
admin.add_view(GroupAdmin)
admin.add_view(GroupMessageAdmin)
admin.add_view(PersonalMessageAdmin)
admin.add_view(RoomAdmin)
admin.add_view(LectureAdmin)
admin.add_view(ExamAdmin)
admin.add_view(ChoiseQuestionAdmin)
admin.add_view(TextQuestionAdmin)
admin.add_view(AnswerAdmin)
admin.add_view(ResultAdmin)
admin.add_view(NotificationAdmin)
# admin.add_view(PassedChoiseAnswersAdmin)
# admin.add_view(PassedTextAnswersAdmin)
