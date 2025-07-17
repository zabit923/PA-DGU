from starlette_admin.contrib.sqla import ModelView


class NotificationAdmin(ModelView):
    label = "Уведомление"
    exclude_fields_from_list = [
        "user",
        "body",
        "is_read",
    ]
    exclude_fields_from_create = [
        "user",
        "is_read",
    ]
    exclude_fields_from_detail = [
        "user",
        "is_read",
    ]
    exclude_fields_from_edit = [
        "user",
        "is_read",
    ]
    searchable_fields = [
        "user.username",
        "title",
        "body",
    ]
