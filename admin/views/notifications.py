from starlette_admin.contrib.sqla import ModelView


class NotificationAdmin(ModelView):
    label = "Уведомление"
    exclude_fields_from_list = [
        "body",
    ]
    exclude_fields_from_edit = [
        "is_read",
    ]
    exclude_fields_from_create = [
        "created_at",
        "updated_at",
    ]
    searchable_fields = [
        "user.username",
        "title",
        "body",
    ]
