from starlette_admin.contrib.sqla import ModelView


class LectureAdmin(ModelView):
    label = "Лекция"
    exclude_fields_from_list = [
        "text",
        "file",
    ]
    exclude_fields_from_create = [
        "created_at",
        "updated_at",
    ]
    searchable_fields = [
        "title",
        "author.username",
    ]
