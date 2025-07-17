from starlette_admin.contrib.sqla import ModelView


class GroupMessageAdmin(ModelView):
    label = "Групповое сообщение"
    exclude_fields_from_list = [
        "users_who_checked",
        "text",
    ]
    exclude_fields_from_create = [
        "users_who_checked",
    ]
    exclude_fields_from_detail = [
        "users_who_checked",
    ]
    exclude_fields_from_edit = [
        "users_who_checked",
    ]
    searchable_fields = [
        "id",
        "sender.username",
        "group.title",
    ]
