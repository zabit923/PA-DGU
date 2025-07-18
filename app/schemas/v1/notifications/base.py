from pydantic import Field

from app.schemas.v1.base import BaseSchema
from app.schemas.v1.users import UserShortSchema


class NotificationDataSchema(BaseSchema):
    title: str = Field(
        description="Заголовок уведомления",
        example="Новое сообщение",
    )
    body: str = Field(
        description="Текст уведомления",
        example="У вас новое сообщение от пользователя.",
    )
    user: "UserShortSchema"
    is_read: bool
