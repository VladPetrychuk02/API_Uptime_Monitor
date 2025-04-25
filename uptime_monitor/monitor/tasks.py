import requests
from celery import shared_task
from django.utils.timezone import now
from .models import MonitoredURL

@shared_task
def check_url_status():
    urls = MonitoredURL.objects.all()
    for url_obj in urls:
        try:
            response = requests.get(url_obj.url, timeout=5)
            status = 'UP' if response.status_code < 400 else 'DOWN'
        except Exception:
            status = 'DOWN'

        if status != url_obj.status:
            # TODO: Email / Webhook alerts here will be later
            pass

        url_obj.status = status
        url_obj.last_checked = now()
        url_obj.save()