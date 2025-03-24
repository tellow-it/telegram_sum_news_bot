import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand

from core.config import Settings
from core.logger import logger
from src.database.postgres.connection import init_models
from src.database.redis.connection import redis_client
from src.handlers import register_base_handlers, bot_commands
from src.handlers.auth_bot.auth import auth_router
from src.handlers.subscription_bot.subscription import subscription_router

# Объект бота
bot = Bot(token=Settings.BOT_TOKEN)


async def main():
    await init_models()
    # Диспетчер
    dp = Dispatcher(storage=RedisStorage(redis_client))
    commands_for_bot = []
    for cmd in bot_commands:
        commands_for_bot.append(BotCommand(command=cmd[0], description=cmd[1]))
    await bot.set_my_commands(commands_for_bot)

    register_base_handlers(dp)
    dp.include_router(auth_router)
    dp.include_router(subscription_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logger.info("Bot started")
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info('Bot stopped')
