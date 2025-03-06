from aiogram import F
from aiogram import Router
from aiogram.filters.command import Command

from src.handlers.help_commands import help_bot, cancel_handler
from src.handlers.auth_bot.auth import start, menu
from src.handlers.subscription_bot.subscription import (
    add_channel,
    remove_channel,
    list_channels,
    update_period_channel
)

bot_commands = (
    ('start', 'Начало работы с ботом'),
    ('menu', 'Меню бота'),
    ('help', 'Помощь с ботом'),
    ('login', 'Регистрация в боте'),
    ('add_channel', 'Добавить канал'),
    ('list_channels', 'Список каналов'),
    ('update_period_channel', 'Изменить период оповещения для канала'),
    ('remove_channel', 'Удалить канал'),
    ('logout', 'Удалить учетную запись из бота'),
)


def register_base_handlers(router: Router) -> None:
    """
    Зарегистрировать хендлеры пользователя
    :param router:
    """
    router.message.register(start, F.text == "Старт")
    router.message.register(menu, F.text == "Меню")

    router.message.register(help_bot, Command(commands=["help"]))
    router.message.register(help_bot, F.text == "Помощь")

    router.message.register(cancel_handler, F.text == "Отмена")

    router.message.register(add_channel, F.text == "Добавить канал")
    router.message.register(remove_channel, F.text == "Удалить канал")
    router.message.register(list_channels, F.text == "Список каналов")
    router.message.register(update_period_channel, F.text == "Изменить период оповещения для канала")
