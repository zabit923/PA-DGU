from sqladmin import ModelView

from core.database.models import Organization


class OrganizationAdmin(ModelView, model=Organization):
    column_list = [Organization.id, Organization.name]
    column_searchable_list = [Organization.name]
    name = "Организация"
    name_plural = "Организации"
    icon = "fa-solid fa-building-columns"
    column_default_sort = [("created_at", True)]
