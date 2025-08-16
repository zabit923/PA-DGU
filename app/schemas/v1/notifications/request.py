from app.schemas.v1.base import BaseRequestSchema


class NotificationCreateSchema(BaseRequestSchema):
    title: str
    body: str
