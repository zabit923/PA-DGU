from sqladmin import ModelView

from core.database.models import Category


class CategoryAdmin(ModelView, model=Category):
    column_list = [
        Category.id,
        Category.title,
        Category.created_at,
    ]
    column_searchable_list = ["title"]
    column_default_sort = [("created_at", True)]
    name = "Категория"
    name_plural = "Категории"
    icon = "fa-solid fa-list"
