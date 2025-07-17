from starlette_admin.contrib.sqla import ModelView


class LectureAdmin(ModelView):
    label = "Лекция"
    exclude_fields_from_list = [
        "author",
        "groups",
        "text",
        "file",
    ]
    exclude_fields_from_create = [
        "author",
        "groups",
    ]
    exclude_fields_from_detail = [
        "author",
        "groups",
    ]
    exclude_fields_from_edit = [
        "author",
        "groups",
    ]
    searchable_fields = [
        "title",
        "author.username",
    ]
