from sqladmin import ModelView

from core.database.models import User


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.username,
        User.first_name,
        User.last_name,
        User.is_teacher,
    ]
    column_searchable_list = [User.username]
    column_default_sort = [("created_at", True)]
    form_excluded_columns = [
        User.member_groups,
        User.lectures,
        User.created_groups,
        User.sent_group_messages,
        User.sent_personal_messages,
        User.rooms,
        User.exams,
        User.results,
    ]
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"
