import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

from monitor import tasks  # noqa: F401

load_dotenv()

app = Celery("uptime_monitor")

app.autodiscover_tasks(["uptime_monitor.monitor"])
app.conf.broker_url = os.getenv("CELERY_BROKER_URL")
app.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND")
app.conf.accept_content = ["json"]
app.conf.task_serializer = "json"

app.conf.beat_schedule = {
    'check-url-status-every-minute': {
        'task': 'monitor.tasks.check_url_status',
        'schedule': crontab(minute='*'),
    },
}
