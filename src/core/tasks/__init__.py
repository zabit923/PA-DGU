from .celery import celery
from .tasks import (
    send_activation_email,
    send_new_exam_email,
    send_new_group_message_email,
    send_new_lecture_notification,
    send_new_private_message_email,
    send_new_result_to_teacher,
)

__all__ = (
    "celery",
    "send_new_lecture_notification",
    "send_activation_email",
    "send_new_group_message_email",
    "send_new_private_message_email",
    "send_new_exam_email",
    "send_new_result_to_teacher",
)
