from starlette_admin.contrib.sqla import ModelView


class NewsAdmin(ModelView):
    label = "Новость"
    exclude_fields_from_list = [
        "text",
        "image",
        "time_to_read",
        "category",
    ]
    exclude_fields_from_create = [
        "category",
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_detail = [
        "category",
    ]
    exclude_fields_from_edit = [
        "category",
    ]
    searchable_fields = [
        "title",
        "category.title",
    ]
