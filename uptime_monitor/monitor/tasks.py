import logging
import requests
from datetime import datetime, timedelta
from celery import shared_task

from uptime_monitor.database import SessionLocal, MonitoredURL, UptimeHistory
from monitor.utils import send_webhook

logger = logging.getLogger(__name__)


@shared_task
def check_url_status():
    db = SessionLocal()
    try:
        urls = db.query(MonitoredURL).all()
        for url_obj in urls:
            now = datetime.utcnow()
            if url_obj.last_checked is None or (
                url_obj.last_checked + timedelta(minutes=url_obj.check_interval) <= now
            ):
                try:
                    response = requests.get(url_obj.url, timeout=5)
                    new_status = "UP" if response.status_code < 400 else "DOWN"
                except Exception:
                    new_status = "DOWN"

                if new_status != url_obj.status:
                    logger.info(f"Status for {url_obj.url} changed to {new_status}")
                    # Логування для вебхуку
                    if url_obj.webhook_url:
                        logger.info(f"Sending webhook for {url_obj.url} with status {new_status}")
                        send_webhook(url_obj.webhook_url, url_obj.url, url_obj.status, new_status)

                url_obj.status = new_status
                url_obj.last_checked = now
                db.add(url_obj)

                db.add(UptimeHistory(
                    monitored_url_id=url_obj.id,
                    status=new_status,
                    checked_at=now,
                    url=url_obj.url,
                    check_interval=url_obj.check_interval
                ))
        db.commit()
    finally:
        db.close()
