from sqladmin import ModelView

from core.database.models import Answer, Exam, ExamResult, PassedAnswer, Question


class ExamAdmin(ModelView, model=Exam):
    column_list = [
        Exam.id,
        Exam.title,
        Exam.groups,
        Exam.author,
        Exam.created_at,
    ]
    column_searchable_list = ["title"]
    form_excluded_columns = [
        Exam.questions,
        Exam.results,
    ]
    column_default_sort = [("created_at", True)]
    name = "Экзамен"
    name_plural = "Экзамены"
    icon = "fa-solid fa-pen"


class QuestionAdmin(ModelView, model=Question):
    column_list = [
        Question.id,
        Question.text,
    ]
    column_searchable_list = ["text"]
    column_default_sort = [("id", True)]
    form_excluded_columns = [Question.answers]
    name = "Вопрос"
    name_plural = "Вопросы"
    icon = "fa-solid fa-circle-question"


class AnswerAdmin(ModelView, model=Answer):
    column_list = [
        Answer.id,
        Answer.text,
        Answer.is_correct,
    ]
    column_default_sort = [("id", True)]
    column_searchable_list = ["text"]
    name = "Ответ"
    name_plural = "Ответы"
    icon = "fa fa-check-circle"


class ResultAdmin(ModelView, model=ExamResult):
    column_list = [
        ExamResult.id,
        ExamResult.exam,
        ExamResult.student,
        ExamResult.score,
    ]
    column_default_sort = [("created_at", True)]
    column_searchable_list = ["student.username"]
    name = "Результат"
    name_plural = "Результаты"
    icon = "fa-solid fa-square-poll-vertical"


class PassedAnswersAdmin(ModelView, model=PassedAnswer):
    column_list = [
        PassedAnswer.id,
        PassedAnswer.exam,
        PassedAnswer.user,
    ]
    column_default_sort = [("created_at", True)]
    name = "Ответ студента"
    name_plural = "Ответы студентов"
    icon = "fa-solid fa-user-check"
