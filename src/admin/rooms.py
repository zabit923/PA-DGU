from sqladmin import ModelView

from core.database.models import PrivateRoom


class RoomAdmin(ModelView, model=PrivateRoom):
    column_list = [
        PrivateRoom.id,
        PrivateRoom.members,
        PrivateRoom.created_at,
    ]
    column_searchable_list = ["id"]
    column_default_sort = [("created_at", True)]
    name = "Комната"
    name_plural = "Комнаты"
    icon = "fa-solid fa-people-arrows"
