from sqlalchemy.orm import Session
from uptime_monitor.database import MonitoredURL, UptimeHistory


def create_monitored_url(db: Session, user_id: int, url: str, check_interval: int, webhook_url: str):
    db_url = MonitoredURL(user_id=user_id, url=url, check_interval=check_interval, webhook_url=webhook_url)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url


def update_monitored_url(db: Session, url_id: int, updated_data: dict):
    url = db.query(MonitoredURL).filter(MonitoredURL.id == url_id).first()
    if not url:
        return None
    for key, value in updated_data.items():
        setattr(url, key, value)
    db.commit()
    db.refresh(url)
    return url


def delete_monitored_url(db: Session, url_id: int):
    url = db.query(MonitoredURL).filter(MonitoredURL.id == url_id).first()
    if not url:
        return None
    db.delete(url)
    db.commit()
    return url


def get_all_monitored_urls(db: Session):
    return db.query(MonitoredURL).all()


def get_uptime_history(db: Session, user_id: int, from_date=None, to_date=None):
    query = (
        db.query(UptimeHistory)
        .join(MonitoredURL, MonitoredURL.id == UptimeHistory.monitored_url_id)
        .filter(MonitoredURL.user_id == user_id)
    )

    if from_date:
        query = query.filter(UptimeHistory.checked_at >= from_date)
    if to_date:
        query = query.filter(UptimeHistory.checked_at <= to_date)

    return query.order_by(UptimeHistory.checked_at.desc()).all()


def update_monitored_url_status(db: Session, url_obj: MonitoredURL, new_status: str):
    url_obj.status = new_status
    db.merge(url_obj)
    db.commit()


def create_uptime_history(db: Session, url_id: int, status: str, checked_at: str, check_interval: int, url: str):
    db_history = UptimeHistory(
        monitored_url_id=url_id,
        status=status,
        checked_at=checked_at,
        url=url,
        check_interval=check_interval
    )
    db.add(db_history)
    db.commit()
