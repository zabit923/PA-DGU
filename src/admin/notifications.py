from sqladmin import ModelView

from core.database.models import Notification


class NotificationAdmin(ModelView, model=Notification):
    column_list = [
        Notification.id,
        Notification.title,
        Notification.created_at,
    ]
    column_searchable_list = ["user.username"]
    column_default_sort = [("created_at", True)]
    name = "уведомление"
    name_plural = "уведомления"
    icon = "fa-solid fa-envelope"
