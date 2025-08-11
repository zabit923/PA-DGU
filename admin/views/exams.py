from starlette_admin.contrib.sqla import ModelView


class ExamAdmin(ModelView):
    label = "Экзамен"
    exclude_fields_from_list = [
        "questions",
        "text_questions",
        "results",
        "passed_text_answers",
        "passed_choice_answers",
        "groups",
    ]
    exclude_fields_from_create = [
        "questions",
        "text_questions",
        "results",
        "passed_text_answers",
        "passed_choice_answers",
        "groups",
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_detail = [
        "questions",
        "text_questions",
        "results",
        "passed_text_answers",
        "passed_choice_answers",
        "groups",
    ]
    exclude_fields_from_edit = [
        "questions",
        "text_questions",
        "results",
        "passed_text_answers",
        "passed_choice_answers",
        "groups",
    ]
    searchable_fields = [
        "title",
        "author.username",
    ]


class QuestionAdmin(ModelView):
    label = "Вопрос"
    exclude_fields_from_list = [
        "answers",
    ]
    exclude_fields_from_create = [
        "answers",
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_detail = [
        "answers",
    ]
    exclude_fields_from_edit = [
        "answers",
    ]
    searchable_fields = [
        "text",
        "exam.title",
    ]


class TextQuestionAdmin(ModelView):
    label = "Текстовый вопрос"
    exclude_fields_from_list = []
    exclude_fields_from_create = [
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_detail = []
    exclude_fields_from_edit = []
    searchable_fields = [
        "text",
        "exam.title",
    ]


class AnswerAdmin(ModelView):
    label = "Ответ"
    exclude_fields_from_create = [
        "created_at",
        "updated_at",
    ]
    searchable_fields = [
        "text",
    ]


class ExamResultAdmin(ModelView):
    label = "Результат"
    exclude_fields_from_list = []
    exclude_fields_from_create = [
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_detail = []
    exclude_fields_from_edit = []
    searchable_fields = [
        "student.username",
        "exam.title",
    ]


class PassedChoiceAnswerAdmin(ModelView):
    label = "Пройденный выборочный ответ"
    exclude_fields_from_list = []
    exclude_fields_from_create = [
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_detail = []
    exclude_fields_from_edit = []
    searchable_fields = [
        "user.username",
        "exam.title",
    ]


class PassedTextAnswerAdmin(ModelView):
    label = "Пройденный текстовый ответ"
    exclude_fields_from_list = []
    exclude_fields_from_create = [
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_detail = []
    exclude_fields_from_edit = []
    searchable_fields = [
        "user.username",
        "exam.title",
    ]
