from sqladmin import ModelView

from core.database.models import PrivateMessage


class PersonalMessageAdmin(ModelView, model=PrivateMessage):
    column_list = [
        PrivateMessage.id,
        PrivateMessage.sender,
        PrivateMessage.room,
        PrivateMessage.created_at,
    ]
    column_searchable_list = ["id"]
    column_default_sort = [("created_at", True)]
    name = "Личное сообщение"
    name_plural = "Личные сообщения"
    icon = "fa-solid fa-comment"
