from starlette_admin.contrib.sqla import ModelView


class RoomAdmin(ModelView):
    label = "Комната"
    exclude_fields_from_list = [
        "messages",
    ]
    exclude_fields_from_create = [
        "messages",
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_detail = [
        "messages",
    ]
    exclude_fields_from_edit = [
        "messages",
    ]
    searchable_fields = [
        "id",
        "members.username",
    ]
