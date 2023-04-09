import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ix.server.settings")

app = Celery("ix")

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.update(
    broker_url="redis://redis:6379/0",
    result_backend="redis://redis:6379/0",
    accept_content=["application/json"],
    task_serializer="json",
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@app.task(bind=True)
def debug_task(self):
    print(f"Celery debug task: {self.request!r}")
