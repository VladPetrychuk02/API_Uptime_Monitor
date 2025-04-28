import requests
from datetime import timedelta
from celery import shared_task
from django.utils.timezone import now
from .models import MonitoredURL, UptimeHistory
from .utils import send_status_email, send_webhook

@shared_task
def check_url_status():
    urls = MonitoredURL.objects.all()
    for url_obj in urls:
        if url_obj.last_checked is None or (url_obj.last_checked + timedelta(minutes=url_obj.check_interval)) <= now():
            try:
                response = requests.get(url_obj.url, timeout=5)
                status = 'UP' if response.status_code < 400 else 'DOWN'
            except Exception:
                status = 'DOWN'

            old_status = url_obj.status
            if status != old_status:
                send_status_email(url_obj.user.email, url_obj.url, old_status, status)

                if url_obj.webhook_url:
                    send_webhook(url_obj.webhook_url, url_obj.url, old_status, status)

            url_obj.status = status
            url_obj.last_checked = now()
            url_obj.save()

            UptimeHistory.objects.create(
                monitored_url=url_obj,
                status=status,
                checked_at=url_obj.last_checked
            )