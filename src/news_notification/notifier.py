import asyncio
import datetime

from datetime import timedelta

from core.logger import logger
from src.repositories.postgres.news_notification import NewsNotificationRepository
from src.repositories.postgres.user_news_subscription import (
    UserNewsSubscriptionRepository
)
from src.repositories.postgres.channel import ChannelRepository

from main import bot


async def send_notifications():
    logger.info("Start sending notifications")
    news_notifications = \
        await NewsNotificationRepository.get_not_send_news_for_notification()
    all_channels = await ChannelRepository.get_all_channels()

    if news_notifications:
        for news_notification in news_notifications:
            user_id = news_notification.user_id
            chat_id = news_notification.user.chat_id
            channel_id = news_notification.news.channel_id

            subscription = await UserNewsSubscriptionRepository.get_subscription(
                user_id=user_id,
                channel_id=channel_id
            )
            if subscription:
                period_notification = subscription.notifications_period
                created_at = news_notification.created_at

                if (datetime.datetime.now() -
                        timedelta(minutes=period_notification) > created_at):
                    channel_name = None
                    for channel in all_channels:
                        if channel.id == channel_id:
                            channel_name = channel.telegram_url
                    summary = news_notification.news.summary

                    link_to_news = news_notification.news.link_to_news
                    text_to_send = (
                        f""
                        f"Канал: {channel_name}\n"
                        f"Ссылка на новость: {link_to_news}\n"
                        f"Время публикации: {created_at}\n"
                        f"Краткая версия новости:\n{summary}\n"
                    )
                    if news_notification.news.params:
                        text_to_send += "Оценка текста: \n"
                        for param in news_notification.news.params:
                            text_to_send += \
                                f"{param["ru_title"]}: {param["ru_content"]}\n"
                    await bot.send_message(chat_id, text_to_send)
                    await NewsNotificationRepository.update_news_notification_status(
                        news_notification_id=news_notification.id,
                        send_status=True
                    )
                    logger.info(f"Successfully sent notification to {chat_id=} {news_notification.id=}")


async def run_notifier():
    while True:
        await send_notifications()
        await asyncio.sleep(30)
