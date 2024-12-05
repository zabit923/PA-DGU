from celery import Celery

from config import settings

celery = Celery(
    "tasks",
    broker=settings.redis.url,
    backend=settings.redis.url,
)

celery.autodiscover_tasks(["tasks"])
