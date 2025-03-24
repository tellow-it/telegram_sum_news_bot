import datetime

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.database.postgres.connection import async_session
from src.database.postgres.models import NewsNotification, News


class NewsNotificationRepository:
    @staticmethod
    async def add_news_notification(user_id: int, news_id: int):
        async with async_session() as session:
            news_notification = NewsNotification(
                user_id=user_id,
                news_id=news_id,
                send_status=False
            )
            session.add(news_notification)
            await session.commit()
            return news_notification

    @staticmethod
    async def update_news_notification_status(news_notification_id: int, send_status: bool):
        async with async_session() as session:
            async with session.begin():
                # Get fresh copy in current session
                result = await session.execute(
                    select(NewsNotification).where(
                        NewsNotification.id == news_notification_id)
                )
                exist_news_notification = result.scalar_one_or_none()

                if not exist_news_notification:
                    raise Exception(
                        f"News notification does not exist for {news_notification_id}"
                    )
                exist_news_notification.send_status = send_status
                exist_news_notification.send_at = datetime.datetime.utcnow()

    @staticmethod
    async def get_not_send_news_for_notification():
        async with async_session() as session:
            result = await session.execute(
                select(NewsNotification).
                where(NewsNotification.send_status == False).
                join(NewsNotification.news).
                where(News.summary.isnot(None)).
                options(joinedload(NewsNotification.news)).
                options(joinedload(NewsNotification.user))
            )
            news_notifications = result.unique().scalars().all()
            return news_notifications
