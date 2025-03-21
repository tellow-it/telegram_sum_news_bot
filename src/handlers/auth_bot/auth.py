from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from core.logger import logger
from src.keyboards.utils import menu_kbd
from src.repositories.postgres.user import UserRepository

auth_router = Router()


@auth_router.message(Command(commands=['start']))
async def start(message: types.Message, ) -> Message:
    return await message.answer(
        'Добро пожаловать в бота. \n\n'
        'С помощью данного бота вы добавить свои новостные каналы '
        'и получать выжимку из них за указанный период времени.\n\n'
        'Доступные команды:\n'
        'Для запуска бота /start \n'
        'Для регистрации в боте /login \n'
        'Для открытия меню /menu \n'
        'Для добавления канала /add_channel \n'
        'Для просмотра списка каналов /list_channels \n'
        'Для изменения периода рассылки для канала /update_period_channel \n'
        'Для удаления канала /remove_channel \n'
        'Для удаления учетной записи в боте /logout \n'
    )


@auth_router.message(Command(commands=['login']))
async def login(message: types.Message, ) -> Message:
    await message.answer("Авторизация в системе...")

    if await UserRepository.check_if_user_exists(telegram_id=message.from_user.id):
        return await message.answer(
            text="Пользователь уже авторизован в системе",
            reply_markup=menu_kbd()
        )

    try:
        _ = await UserRepository.create_user(telegram_id=message.from_user.id)
        return await message.answer(
            text="Пользователь успешно авторизирован!",
            reply_markup=menu_kbd()
        )
    except Exception as e:
        logger.error(e)
        return await message.answer(
            text="Не удалось создать пользователя. "
                 "Скорее всего пользователь уже существует!",
            reply_markup=ReplyKeyboardRemove()
        )


@auth_router.message(Command(commands=['logout']))
async def logout(message: types.Message, ) -> Message:
    await message.answer(
        text="Удаление пользователя...",
        reply_markup=ReplyKeyboardRemove()
    )
    try:
        await UserRepository.delete_user(telegram_id=message.from_user.id)
        return await message.answer(
            text="Пользователь успешно удален!",
            eeply_markup=ReplyKeyboardRemove()
        )
    except Exception as e:
        logger.error(e)
        return await message.answer(
            text="Пользователь не найден!",
            reply_markup=ReplyKeyboardRemove()
        )


@auth_router.message(Command(commands=['menu']))
async def menu(message: types.Message, ) -> Message:
    if not await UserRepository.check_if_user_exists(telegram_id=message.from_user.id):
        return await message.answer(
            text="Пользователь еще не авторизован в системе. "
                 "Нажмите или введите команду /login",
            reply_markup=ReplyKeyboardRemove()
        )
    return await message.answer(
        text="Меню",
        reply_markup=menu_kbd()
    )
