import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import ForeignKey


DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class MonitoredURL(Base):
    __tablename__ = "monitored_urls"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="urls")
    url = Column(String, index=True)
    check_interval = Column(Integer, default=5)
    status = Column(String, default="UNKNOWN")
    last_checked = Column(DateTime)
    webhook_url = Column(String, nullable=True)

    history = relationship("UptimeHistory", back_populates="monitored_url")


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    urls = relationship("MonitoredURL", back_populates="user")


class UptimeHistory(Base):
    __tablename__ = "uptime_history"
    id = Column(Integer, primary_key=True, index=True)
    monitored_url_id = Column(Integer, ForeignKey("monitored_urls.id"))
    status = Column(String)
    checked_at = Column(DateTime)
    url = Column(String)
    check_interval = Column(Integer)

    monitored_url = relationship("MonitoredURL", back_populates="history")
