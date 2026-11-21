import os

from celery import Celery

REDIS_URL = os.getenv(
    "REDIS_URL"
)

celery_app = Celery(
    "inen",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.autodiscover_tasks(
    ["app.tasks"]
)