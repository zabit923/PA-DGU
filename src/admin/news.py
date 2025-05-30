from sqladmin import ModelView

from core.database.models import News


class NewsAdmin(ModelView, model=News):
    column_list = [
        News.id,
        News.title,
        News.created_at,
    ]
    column_searchable_list = ["title"]
    column_default_sort = [("created_at", True)]
    name = "Новость"
    name_plural = "Новости"
    icon = "fa-solid fa-newspaper"
