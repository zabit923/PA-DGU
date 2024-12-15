from sqladmin import ModelView

from core.database.models import Lecture


class LectureAdmin(ModelView, model=Lecture):
    column_list = [
        Lecture.id,
        Lecture.title,
        Lecture.created_at,
    ]
    column_searchable_list = ["id"]
    column_default_sort = [("created_at", True)]
    name = "Лекция"
    name_plural = "Лекции"
    icon = "fa-solid fa-book"
