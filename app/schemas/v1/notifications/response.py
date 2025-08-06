from typing import TYPE_CHECKING, Any, Dict

from app.schemas.v1.base import BaseResponseSchema, BaseSchema

if TYPE_CHECKING:
    from app.schemas import UserShortSchema


class NotificationResponseSchema(BaseSchema):
    title: str
    body: str
    user: "UserShortSchema"
    is_read: bool


class NotificationListResponseSchema(BaseResponseSchema):
    message: str = "Список уведомлений успешно получен"
    data: Dict[str, Any]
