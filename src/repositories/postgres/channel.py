from sqlalchemy import select

from src.database.postgres.connection import async_session
from src.database.postgres.models import Channel


class ChannelRepository:
    @staticmethod
    async def get_all_channels():
        async with async_session() as session:
            result = await session.execute(select(Channel))
            return result.scalars().all()

    @staticmethod
    async def get_joined_channels():
        async with async_session() as session:
            result = await session.execute(
                select(Channel).
                where(Channel.join_status == True)
            )
            return result.scalars().all()

    @staticmethod
    async def get_not_joined_channels():
        async with async_session() as session:
            result = await session.execute(
                select(Channel).
                where(Channel.join_status == False)
            )
            return result.scalars().all()

    @staticmethod
    async def get_channel(telegram_url: str):
        async with async_session() as session:
            result = await session.execute(
                select(Channel).
                where(Channel.telegram_url == telegram_url)
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def create_channel(telegram_url: str):
        exist_news_channel = await ChannelRepository.get_channel(telegram_url)
        if not exist_news_channel:
            async with async_session() as session:
                news_channel = Channel(
                    telegram_url=telegram_url,
                    join_status=False
                )
                session.add(news_channel)
                await session.commit()
                return news_channel
        return exist_news_channel

    @staticmethod
    async def change_join_status(telegram_url: str, new_status: bool):
        async with async_session() as session:
            async with session.begin():
                # Get fresh copy in current session
                result = await session.execute(
                    select(Channel).where(Channel.telegram_url == telegram_url)
                )
                exist_news_channel = result.scalar_one_or_none()

                if not exist_news_channel:
                    raise Exception(
                        f"News Channel with telegram_url {telegram_url} doesn't exist"
                    )

                exist_news_channel.join_status = new_status

    @staticmethod
    async def delete_channel(telegram_url: str):
        async with async_session() as session:
            news_channel = await ChannelRepository.get_channel(
                telegram_url=telegram_url
            )
            if not news_channel:
                raise Exception(
                    f"News Channel with telegram_url {telegram_url} doesn't exist"
                )
            await session.delete(news_channel)
            await session.commit()
