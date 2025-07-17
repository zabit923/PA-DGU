from starlette_admin.contrib.sqla import ModelView


class PersonalMessageAdmin(ModelView):
    label = "Личное сообщение"
    exclude_fields_from_list = [
        "text",
        "is_readed",
    ]
    exclude_fields_from_create = [
        "is_readed",
    ]
    exclude_fields_from_detail = [
        "is_readed",
    ]
    exclude_fields_from_edit = [
        "is_readed",
    ]
    searchable_fields = [
        "id",
        "sender.username",
        "room.id",
    ]
