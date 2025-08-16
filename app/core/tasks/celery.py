from celery import Celery
from celery.schedules import crontab
from app.core.settings import settings

celery = Celery(
    "personal_accounts",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery.autodiscover_tasks()

celery.conf.beat_schedule = {
    "check_exams_for_starting": {
        "task": "app.core.tasks.periodic_tasks.check_exams_for_starting",
        "schedule": crontab(minute="*/1"),
    },
    "check_ending_exams": {
        "task": "app.core.tasks.periodic_tasks.check_exams_for_ending",
        "schedule": crontab(minute="*/1"),
    },
}
celery.conf.timezone = "UTC"
