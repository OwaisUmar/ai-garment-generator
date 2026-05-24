from celery import Celery

from config.settings import settings

celery_app = Celery(
    'fashion_generator',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

import tasks.generation_task

# celery_app.autodiscover_tasks(['tasks'])