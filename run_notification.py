import asyncio
import time

from core.logger import logger
from src.news_notification.notifier import run_notifier

try:
    logger.info("Starting notification...")
    asyncio.run(run_notifier())
except (KeyboardInterrupt, SystemExit):
    logger.info('Stop notification')
