from celery import Celery
from celery.schedules import crontab

from config import RedisSettings

celery = Celery(
    "personal_accounts",
    broker=RedisSettings().url,
    backend=RedisSettings().url,
)

celery.autodiscover_tasks()

celery.conf.beat_schedule = {
    "check_exams_for_starting": {
        "task": "core.tasks.tasks.check_exams_for_starting",
        "schedule": crontab(minute="*/5"),
    },
    "check_ending_exams": {
        "task": "core.tasks.tasks.check_exams_for_ending",
        "schedule": crontab(minute="*/5"),
    },
}
celery.conf.timezone = "UTC"
