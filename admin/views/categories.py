from starlette_admin.contrib.sqla import ModelView


class CategoryAdmin(ModelView):
    label = "Категория"
    exclude_fields_from_list = [
        "newses",
    ]
    exclude_fields_from_create = [
        "newses",
    ]
    exclude_fields_from_detail = [
        "newses",
    ]
    exclude_fields_from_edit = [
        "newses",
    ]
    searchable_fields = [
        "title",
    ]
