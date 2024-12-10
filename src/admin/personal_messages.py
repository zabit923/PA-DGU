from sqladmin import ModelView

from core.database.models import PersonalMessage


class PersonalMessageAdmin(ModelView, model=PersonalMessage):
    column_list = [
        PersonalMessage.id,
        PersonalMessage.sender,
        PersonalMessage.room,
        PersonalMessage.created_at,
    ]
    column_searchable_list = ["id"]
    column_default_sort = [("created_at", True)]
    name = "Личное сообщение"
    name_plural = "Личные сообщения"
    icon = "fa-solid fa-comment"
