from sqladmin import ModelView

from core.database.models import GroupMessage


class GroupMessageAdmin(ModelView, model=GroupMessage):
    column_list = [
        GroupMessage.id,
        GroupMessage.sender,
        GroupMessage.group,
        GroupMessage.created_at,
    ]
    column_searchable_list = ["id"]
    column_default_sort = [("created_at", True)]
    name = "Групповое сообщение"
    name_plural = "Групповые сообщения"
    icon = "fa-solid fa-comments"
