from sqladmin import ModelView

from core.database.models import Answer, Exam, ExamResult, Question, TextQuestion


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
        Exam.text_questions,
        Exam.results,
    ]
    column_default_sort = [("created_at", True)]
    name = "Экзамен"
    name_plural = "Экзамены"
    icon = "fa-solid fa-pen"


class ChoiseQuestionAdmin(ModelView, model=Question):
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


class TextQuestionAdmin(ModelView, model=TextQuestion):
    column_list = [
        TextQuestion.id,
        TextQuestion.text,
    ]
    column_searchable_list = ["text"]
    column_default_sort = [("id", True)]
    form_excluded_columns = [Question.answers]
    name = "Текстовый вопрос"
    name_plural = "Текстовые вопросы"
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
