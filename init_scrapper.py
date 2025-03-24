import asyncio

from telethon import TelegramClient
from core.config import Settings
from core.logger import logger

API_ID = Settings.API_ID
API_HASH = Settings.API_HASH
SESSION_NAME = Settings.SESSION_NAME

CLIENT = TelegramClient(SESSION_NAME, API_ID, API_HASH)


async def init_session():
    await CLIENT.start()
    await CLIENT.run_until_disconnected()


try:
    logger.info("Starting scraper...")
    asyncio.run(init_session())
except (KeyboardInterrupt, SystemExit):
    logger.info('Bot stopped')
