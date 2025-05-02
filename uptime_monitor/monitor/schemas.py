from pydantic import BaseModel
from datetime import datetime


class MonitoredURLBase(BaseModel):
    url: str
    check_interval: int
    webhook_url: str


class MonitoredURLCreate(MonitoredURLBase):
    user_id: int


class MonitoredURL(MonitoredURLBase):
    id: int
    status: str
    last_checked: datetime | None = None

    model_config = {
        "from_attributes": True
    }


class UptimeHistory(BaseModel):
    id: int
    url: str
    monitored_url_id: int
    status: str
    checked_at: datetime
    check_interval: int

    model_config = {
        "from_attributes": True
    }
