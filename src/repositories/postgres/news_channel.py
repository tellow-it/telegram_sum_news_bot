from sqlalchemy import select

from src.database.postgres.connection import async_session
from src.database.postgres.models import NewsChannel


class NewsChannelRepository:
    @staticmethod
    async def create_news_channel(telegram_url: str):
        async with async_session() as session:
            news_channel = NewsChannel(telegram_url=telegram_url)
            session.add(news_channel)
            await session.commit()
            await session.refresh(news_channel)
            return news_channel

    @staticmethod
    async def check_if_news_channel_exists(telegram_url: str):
        async with async_session() as session:
            result = await session.execute(
                select(NewsChannel).
                where(NewsChannel.telegram_url == telegram_url)
            )
            if result.scalar_one_or_none():
                return True
            return False

    @staticmethod
    async def get_all_new_channels():
        async with async_session() as session:
            result = await session.execute(select(NewsChannel))
            return result.scalars().all()

    @staticmethod
    async def get_news_channel(telegram_url: str):
        async with async_session() as session:
            result = await session.execute(
                select(NewsChannel).
                where(NewsChannel.telegram_url == telegram_url)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def delete_news_channel(telegram_url: str):
        async with async_session() as session:
            news_channel = await NewsChannelRepository.get_news_channel(
                telegram_url=telegram_url
            )
            if not news_channel:
                raise Exception(
                    f"News Channel with telegram_url {telegram_url} doesn't exist"
                )
            await session.delete(news_channel)
            await session.commit()
