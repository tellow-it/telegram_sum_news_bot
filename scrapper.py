from telethon import TelegramClient, events
import asyncio
from telethon.tl.functions.channels import JoinChannelRequest, GetParticipantRequest
from telethon.tl.types import (
    ChannelParticipantSelf,
    ChannelParticipantAdmin,
    ChannelParticipantCreator
)

from core.config import Settings
from core.logger import logger
from src.repositories.postgres.channel import ChannelRepository
from src.repositories.postgres.news import NewsRepository
from src.repositories.postgres.news_notification import NewsNotificationRepository
from src.repositories.postgres.user_news_subscription import (
    UserNewsSubscriptionRepository
)

API_ID = Settings.API_ID
API_HASH = Settings.API_HASH
SESSION_NAME = Settings.SESSION_NAME

CLIENT = TelegramClient(SESSION_NAME, API_ID, API_HASH)
EVENT_HANDLER = None


async def listen_to_channels():
    global EVENT_HANDLER, CLIENT

    channels = await ChannelRepository.get_joined_channels()

    if not channels:
        logger.info("Channels not found.")
        return

    channels_urls = [channel.telegram_url for channel in channels]
    logger.info(f"Updated list of channels for scrapper: {channels_urls}")

    if EVENT_HANDLER:
        CLIENT.remove_event_handler(EVENT_HANDLER)
        logger.info("Old EVENT_HANDLER is removed.")

        await asyncio.sleep(1)

    async def handler(event):
        chat = await event.get_chat()
        username = chat.username
        message_id = event.message.id
        message = event.message.text
        message_url = f"https://t.me/{username}/{message_id}"
        channel = await ChannelRepository.get_channel(f"https://t.me/{username}")
        channel_id = channel.id

        subs = await UserNewsSubscriptionRepository.get_users_subs_by_channel(
            channel_id=channel_id
        )
        if subs:
            news_db = await NewsRepository.add_news(
                channel_id=channel_id,
                link_to_news=message_url,
                message=message
            )
            user_ids = []
            for sub in subs:
                user_ids.append(sub.user_id)
                await NewsNotificationRepository.add_news_notification(
                    user_id=sub.user_id,
                    news_id=news_db.id
                )

            logger.info(
                f"{channel_id=} {message_url=} {user_ids=} "
                f"message={message[:50]}..."
            )

    EVENT_HANDLER = handler
    CLIENT.add_event_handler(handler, events.NewMessage(chats=channels_urls))

    logger.info("Updated EVENT HANDLER is started.")


async def is_member(channel_username):
    try:
        participant = await CLIENT(GetParticipantRequest(channel_username, "me"))
        if isinstance(
                participant.participant,
                (
                    ChannelParticipantSelf,
                    ChannelParticipantAdmin,
                    ChannelParticipantCreator
                )
        ):
            return True
    except Exception as err:
        logger.error(err)
        return False
    return False


async def join_to_channel(telegram_url: str):
    if await is_member(telegram_url):
        logger.info("Already joined.")
    else:
        try:
            logger.info("Joining to channel")
            await CLIENT(JoinChannelRequest(telegram_url))
            logger.info("Update status to true")
            await ChannelRepository.change_join_status(
                telegram_url=telegram_url,
                new_status=True
            )
            logger.info("Successfully joined to channel")
        except Exception as err:
            logger.info("Some error while joining to channel")


async def join_to_not_subs_channels():
    channels = await ChannelRepository.get_not_joined_channels()

    if not channels:
        logger.info("Channels for joining not found")
        return

    channels_urls = [channel.telegram_url for channel in channels]
    logger.info(f"List channels for joining: {channels_urls}")

    for channel_url in channels_urls:
        await join_to_channel(channel_url)


async def run_joining_periodically():
    while True:
        await join_to_not_subs_channels()
        await asyncio.sleep(30)  # 30 секунд


async def update_channels_periodically():
    while True:
        await listen_to_channels()
        await asyncio.sleep(30)  # 30 секунд


async def run_scrapper():
    await CLIENT.start()
    asyncio.create_task(run_joining_periodically())
    asyncio.create_task(update_channels_periodically())
    await CLIENT.run_until_disconnected()
