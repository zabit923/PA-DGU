from sqladmin import ModelView

from core.database.models import Answer, Exam, Question


class ExamAdmin(ModelView, model=Exam):
    column_list = [
        Exam.id,
        Exam.title,
        Exam.groups,
        Exam.author,
        Exam.created_at,
    ]
    column_searchable_list = ["title"]
    column_default_sort = [("created_at", True)]
    name = "Экзамен"
    name_plural = "Экзамены"
    icon = "fa-solid fa-pen"


class QuestionAdmin(ModelView, model=Question):
    column_list = [
        Question.id,
        Question.text,
    ]
    column_searchable_list = ["exam.title"]
    name = "Вопрос"
    name_plural = "Вопросы"
    icon = "fa-solid fa-circle-question"


class AnswerAdmin(ModelView, model=Answer):
    column_list = [
        Answer.id,
        Answer.text,
        Answer.is_correct,
    ]
    name = "Ответ"
    name_plural = "Ответы"
    icon = "fa fa-check-circle"
