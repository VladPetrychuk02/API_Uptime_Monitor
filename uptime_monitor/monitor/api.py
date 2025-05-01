from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from sqlalchemy import func

from uptime_monitor.auth import get_current_user
from uptime_monitor.database import SessionLocal, User
from uptime_monitor.database import MonitoredURL as MonitoredURLModel, UptimeHistory as UptimeHistoryModel
from monitor.schemas import MonitoredURLCreate, MonitoredURL, UptimeHistory as UptimeHistorySchema

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/urls/", response_model=MonitoredURL)
def create_monitored_url(url: MonitoredURLCreate, db: Session = Depends(get_db)):
    db_url = MonitoredURLModel(
        url=url.url,
        check_interval=url.check_interval,
        webhook_url=url.webhook_url,
        user_id=url.user_id
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url


@router.get("/urls/", response_model=list[MonitoredURL])
def get_urls(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(MonitoredURLModel).filter(MonitoredURLModel.user_id == current_user.id).all()


@router.get("/history/", response_model=list[UptimeHistorySchema])
def get_uptime_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to")
):
    query = db.query(UptimeHistoryModel).join(MonitoredURLModel, MonitoredURLModel.id == UptimeHistoryModel.monitored_url_id).filter(
        MonitoredURLModel.user_id == current_user.id
    )

    if from_date:
        query = query.filter(UptimeHistoryModel.checked_at >= from_date)
    if to_date:
        query = query.filter(UptimeHistoryModel.checked_at <= to_date)

    return query.order_by(UptimeHistoryModel.checked_at.desc()).all()


@router.get("/stats/")
def get_uptime_status_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = (
        db.query(UptimeHistoryModel.status, func.count().label("count"))
        .select_from(UptimeHistoryModel)
        .join(MonitoredURLModel, MonitoredURLModel.id == UptimeHistoryModel.monitored_url_id)
        .filter(MonitoredURLModel.user_id == current_user.id)
        .group_by(UptimeHistoryModel.status)
        .all()
    )

    stats = {row.status: row.count for row in result}

    for status in ["UP", "DOWN", "UNKNOWN"]:
        stats.setdefault(status, 0)

    return stats
