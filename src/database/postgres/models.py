from sqlalchemy import (
    Column, Integer, ForeignKey, DateTime, String
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_url = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class NewsChannel(Base):
    __tablename__ = 'news_channels'
    id = Column(Integer, primary_key=True)
    telegram_channel_url = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserChannelSubscription(Base):
    __tablename__ = 'user_channel_subscriptions'
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    channel_id = Column(Integer, ForeignKey('news_channels.id', ondelete='CASCADE'), primary_key=True)
    notifications_period = Column(Integer, nullable=False)

    user = relationship("User", backref="subscriptions")
    channel = relationship("NewsChannel", backref="subscribers")


class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey('news_channels.id', ondelete='CASCADE'))
    link_to_news = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    text = Column(String, nullable=False)
    summary = Column(String, nullable=False)

    channel = relationship("NewsChannel", backref="news")
