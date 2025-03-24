from sqlalchemy import (
    Column, Integer, ForeignKey, DateTime, String, BigInteger, Boolean, JSON, text
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, unique=True, nullable=False, primary_key=True)
    chat_id = Column(BigInteger, unique=True, nullable=False)
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        server_default=text("TIMEZONE('utc', now())")
    )


class Channel(Base):
    __tablename__ = 'channels'
    id = Column(Integer, primary_key=True)
    telegram_url = Column(String, unique=True, nullable=False)
    join_status = Column(Boolean, nullable=False, server_default=text("FALSE"))
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        server_default=text("TIMEZONE('utc', now())")
    )


class UserChannelSubscription(Base):
    __tablename__ = 'user_channel_subscriptions'
    user_id = Column(
        BigInteger,
        ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True
    )
    channel_id = Column(
        Integer,
        ForeignKey('channels.id', ondelete='CASCADE'),
        primary_key=True
    )
    notifications_period = Column(Integer, nullable=False)
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        server_default=text("TIMEZONE('utc', now())")
    )

    user = relationship("User", backref="subscriptions")
    channel = relationship("Channel", backref="subscribers")


class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey('channels.id', ondelete='CASCADE'))
    link_to_news = Column(String, unique=True, nullable=False)
    message = Column(String, nullable=False)
    summary = Column(String, nullable=True)
    params = Column(JSON, nullable=True)
    published_at = Column(
        DateTime,
        default=datetime.utcnow,
        server_default=text("TIMEZONE('utc', now())")
    )
    channel = relationship("Channel", backref="news")


class NewsNotification(Base):
    __tablename__ = 'news_notifications'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'))
    news_id = Column(Integer, ForeignKey('news.id', ondelete='CASCADE'))
    send_status = Column(Boolean, nullable=False, server_default=text("FALSE"))
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        server_default=text("TIMEZONE('utc', now())")
    )
    send_at = Column(DateTime, nullable=True)

    user = relationship("User", backref="notifications")
    news = relationship("News", backref="notifications")
