from starlette_admin.contrib.sqla import ModelView


class NotificationAdmin(ModelView):
    label = "Уведомление"
    exclude_fields_from_list = [
        "body",
    ]
    exclude_fields_from_edit = [
        "is_read",
    ]
    searchable_fields = [
        "user.username",
        "title",
        "body",
    ]
