import asyncio
import time

from core.logger import logger
from scrapper import run_scrapper

try:
    time.sleep(10)
    logger.info("Starting scraper...")
    asyncio.run(run_scrapper())
except (KeyboardInterrupt, SystemExit):
    logger.info('Stop scraping')
