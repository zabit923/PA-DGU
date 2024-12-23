from celery import Celery

from config import RedisSettings

celery = Celery(
    "personal_accounts",
    broker=RedisSettings().url,
    backend=RedisSettings().url,
)

celery.autodiscover_tasks()
