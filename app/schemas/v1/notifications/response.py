from app.schemas.v1.base import BaseResponseSchema, BaseSchema
from app.schemas.v1.pagination import Page
from app.schemas.v1.users import UserShortSchema


class NotificationResponseSchema(BaseSchema):
    title: str
    body: str
    user: "UserShortSchema"
    is_read: bool


class NotificationListResponseSchema(BaseResponseSchema):
    message: str = "Список уведомлений успешно получен"
    data: Page[NotificationResponseSchema]
