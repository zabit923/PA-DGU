from sqladmin import ModelView

from core.database.models import Group


class GroupAdmin(ModelView, model=Group):
    column_list = [
        Group.id,
        Group.course,
        Group.facult,
        Group.subgroup,
        Group.curator,
        Group.created_at,
    ]
    column_searchable_list = ["curator.username"]
    column_default_sort = [("created_at", True)]
    form_excluded_columns = [
        Group.lectures,
        Group.group_messages,
    ]
    name = "Группа"
    name_plural = "Группы"
    icon = "fa fa-address-card"
