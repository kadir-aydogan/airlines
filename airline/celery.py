import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "airline.settings")
app = Celery("airline")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()