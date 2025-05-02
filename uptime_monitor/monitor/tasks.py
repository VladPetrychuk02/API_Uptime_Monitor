import logging
import requests
from datetime import datetime, timedelta
from celery import shared_task

from uptime_monitor.database import SessionLocal, MonitoredURL, UptimeHistory
from monitor.utils import send_webhook


logger = logging.getLogger(__name__)

class URLStatusChecker:
    def __init__(self, url_obj):
        self.url_obj = url_obj
        self.now = datetime.utcnow()

    def check_url(self):
        try:
            response = requests.get(self.url_obj.url, timeout=5)
            return "UP" if response.status_code < 400 else "DOWN"
        except Exception:
            return "DOWN"

    def update_status(self, new_status):
        self.url_obj.status = new_status
        self.url_obj.last_checked = self.now
        db = SessionLocal()

        db.merge(self.url_obj)
        db.flush() 

        db.add(UptimeHistory(
            monitored_url_id=self.url_obj.id,
            status=new_status,
            checked_at=self.now,
            url=self.url_obj.url,
            check_interval=self.url_obj.check_interval
        ))
        db.commit()

    def send_webhook_alert(self, new_status):
        if self.url_obj.webhook_url:
            logger.info(f"Sending webhook for {self.url_obj.url} with status {new_status}")
            send_webhook(self.url_obj.webhook_url, self.url_obj.url, self.url_obj.status, new_status)


@shared_task
def check_url_status():
    db = SessionLocal()
    try:
        urls = db.query(MonitoredURL).all()
        for url_obj in urls:
            checker = URLStatusChecker(url_obj)
            if url_obj.last_checked is None or (url_obj.last_checked + timedelta(minutes=url_obj.check_interval)) <= checker.now:
                new_status = checker.check_url()

                if new_status != url_obj.status:
                    logger.info(f"Status for {url_obj.url} changed to {new_status}")
                    checker.send_webhook_alert(new_status)

                checker.update_status(new_status)
    finally:
        db.close()
