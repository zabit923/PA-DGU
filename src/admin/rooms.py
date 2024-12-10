from sqladmin import ModelView

from core.database.models import PersonalRoom


class RoomAdmin(ModelView, model=PersonalRoom):
    column_list = [
        PersonalRoom.id,
        PersonalRoom.members,
        PersonalRoom.created_at,
    ]
    column_searchable_list = ["id"]
    column_default_sort = [("created_at", True)]
    name = "Комната"
    name_plural = "Комнаты"
    icon = "fa-solid fa-people-arrows"
