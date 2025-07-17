from starlette_admin.contrib.sqla import ModelView


class GroupAdmin(ModelView):
    label = "Группы"
    exclude_fields_from_list = [
        "invite_token",
        "lectures",
        "members",
        "group_messages",
        "exams",
        "methodist_id",
    ]
    exclude_fields_from_create = [
        "invite_token",
        "lectures",
        "members",
        "group_messages",
        "exams",
        "methodist_id",
    ]
    exclude_fields_from_detail = [
        "invite_token",
        "lectures",
        "members",
        "group_messages",
        "exams",
        "methodist_id",
    ]
    exclude_fields_from_edit = [
        "invite_token",
        "lectures",
        "members",
        "group_messages",
        "exams",
        "methodist_id",
    ]
    searchable_fields = [
        "methodist.username",
    ]
