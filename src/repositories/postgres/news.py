from src.database.postgres.connection import async_session
from src.database.postgres.models import News


class NewsRepository:
    @staticmethod
    async def add_news(channel_id: int, link_to_news: str, text: str):
        async with async_session() as session:
            news = News(channel_id=channel_id, link_to_news=link_to_news, text=text)
            session.add(news)
            await session.commit()
            await session.refresh(news)
            return news
