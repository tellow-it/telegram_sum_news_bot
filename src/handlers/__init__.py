from aiogram import F
from aiogram import Router
from aiogram.filters.command import Command

from src.handlers.help_commands import help_bot
from src.handlers.start_bot.start import start
# from src.handlers.main_part_bot.main_part import (
#     login,
#     menu,
#     add_channel,
#     list_channels,
#     update_period_channel,
#     remove_channel,
#     logout
# )

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
    router.message.register(start, F.text == 'Старт')

    router.message.register(help_bot, Command(commands=['help']))
    router.message.register(help_bot, F.text == 'Помощь')
