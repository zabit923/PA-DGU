from typing import Any, Dict

from starlette.requests import Request
from starlette_admin.contrib.sqla import ModelView

from app.core.security.password import pwd_context


class UserAdmin(ModelView):
    label = "Пользователи"
    exclude_fields_from_create = [
        "created_at",
        "updated_at",
        "created_groups",
        "lectures",
        "sent_group_messages",
        "sent_personal_messages",
        "rooms",
        "exams",
        "results",
        "passed_choice_answers",
        "passed_text_answers",
        "notifications",
        "checked_messages",
        "member_groups",
    ]
    exclude_fields_from_list = [
        "password",
        "image",
        "is_online",
        "is_verified",
        "ignore_messages",
        "created_groups",
        "lectures",
        "sent_group_messages",
        "sent_personal_messages",
        "rooms",
        "exams",
        "results",
        "passed_choice_answers",
        "passed_text_answers",
        "notifications",
        "checked_messages",
        "member_groups",
    ]
    exclude_fields_from_edit = [
        "created_groups",
        "lectures",
        "sent_group_messages",
        "sent_personal_messages",
        "rooms",
        "exams",
        "results",
        "passed_choice_answers",
        "passed_text_answers",
        "notifications",
        "checked_messages",
        "member_groups",
    ]
    exclude_fields_from_detail = [
        "created_groups",
        "lectures",
        "sent_group_messages",
        "sent_personal_messages",
        "rooms",
        "exams",
        "results",
        "passed_choice_answers",
        "passed_text_answers",
        "notifications",
        "checked_messages",
        "member_groups",
    ]
    searchable_fields = [
        "username",
        "email",
        "first_name",
        "last_name",
    ]

    async def create(self, request: Request, data: Dict[str, Any]) -> Any:
        if "password" in data:
            data["password"] = pwd_context.hash(data["password"])
        return await super().create(request, data)

    async def edit(self, request: Request, pk: Any, data: Dict[str, Any]) -> Any:
        if "password" in data:
            data["password"] = pwd_context.hash(data["password"])
        return await super().edit(request, pk, data)
