from .celery import celery
from .tasks import send_activation_email, send_new_lecture_notification

__all__ = ("celery", "send_new_lecture_notification", "send_activation_email")
