from aiogram import types, Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from core.logger import logger
from src.keyboards.utils import cancel_kbd, menu_kbd
from src.repositories.postgres.news_channel import NewsChannelRepository
from src.repositories.postgres.user import UserRepository
from src.handlers.subscription_bot.steps import (
    AddNewsChannelForm,
    UpdateNotificationPeriodForm,
    RemoveNewsChannelForm
)
from src.repositories.postgres.user_news_subscription import UserNewsSubscriptionRepository
from src.repositories.redis import RedisRepository
from src.utils.subscription import is_valid_url

subscription_router = Router()


@subscription_router.message(Command(commands=['add_channel']))
async def add_channel(message: types.Message, state: FSMContext) -> Message:
    if not await UserRepository.check_if_user_exists(telegram_id=message.from_user.id):
        return await message.answer(
            "Пользователь еще не авторизован в системе. "
            "Нажмите или введите команду /login",
            reply_markup=ReplyKeyboardRemove()
        )
    await message.answer("Пришлите ссылку на тг канал", reply_markup=cancel_kbd())
    await state.set_state(AddNewsChannelForm.GET_NEWS_CHANNEL)


@subscription_router.message(AddNewsChannelForm.GET_NEWS_CHANNEL)
async def get_news_channel_for_adding_channel(message: types.Message, state: FSMContext) -> Message:
    if not await UserRepository.check_if_user_exists(telegram_id=message.from_user.id):
        return await message.answer(
            "Пользователь еще не авторизован в системе. "
            "Нажмите или введите команду /login",
            reply_markup=ReplyKeyboardRemove()
        )
    await message.answer(f"Вы указали ссылку на канал: {message.text}!")
    if message.text and is_valid_url(message.text):  # check input val
        await RedisRepository.set_value(f'add_channel:news_channel:user_id:{message.from_user.id}', message.text)
        await message.answer("Введите период оповещения для данного канала", reply_markup=cancel_kbd())
        await state.set_state(AddNewsChannelForm.GET_NOTIFICATION_PERIOD)
    else:
        await message.answer("Введена некорректна ссылка, попробуйте еще раз", reply_markup=cancel_kbd())
        await state.set_state(AddNewsChannelForm.GET_NEWS_CHANNEL)


@subscription_router.message(AddNewsChannelForm.GET_NOTIFICATION_PERIOD)
async def get_notification_period_for_adding_channel(message: types.Message, state: FSMContext) -> Message:
    if not await UserRepository.check_if_user_exists(telegram_id=message.from_user.id):
        return await message.answer(
            "Пользователь еще не авторизован в системе. "
            "Нажмите или введите команду /login",
            reply_markup=ReplyKeyboardRemove()
        )
    await message.answer(f"Вы ввели период: {message.text}!")
    if message.text and str(message.text).isnumeric():  # check input val
        await RedisRepository.set_value(f'add_channel:period:user_id:{message.from_user.id}', int(message.text))
        name_news_channel_from_user = await RedisRepository.get_value(
            f'add_channel:news_channel:user_id:{message.from_user.id}')
        notification_period_from_user = await RedisRepository.get_value(
            f'add_channel:period:user_id:{message.from_user.id}')
        try:
            user_db = await UserRepository.get_user(telegram_id=message.from_user.id)
            news_channel = await NewsChannelRepository.create_news_channel(telegram_url=name_news_channel_from_user)
            _ = await UserNewsSubscriptionRepository.add_subscription(
                user_id=user_db.id,
                channel_id=news_channel.id,
                notification_period=int(notification_period_from_user)
            )
            await message.answer(
                text="Подписка успешно добавлена!",
                reply_markup=menu_kbd()
            )
            await state.clear()
        except Exception as e:
            logger.error(e)
            await message.answer(
                text="Не удалось добавить подписку! "
                     "Возможного для данного пользователя подписка на этот канал уже добавлена",
                reply_markup=menu_kbd()
            )
    else:
        await message.answer("Введен некорректный период, попробуйте еще раз", reply_markup=cancel_kbd())
        await state.set_state(AddNewsChannelForm.GET_NOTIFICATION_PERIOD)


@subscription_router.message(Command(commands=['list_channels']))
async def list_channels(message: types.Message, state: FSMContext) -> Message:
    if not await UserRepository.check_if_user_exists(telegram_id=message.from_user.id):
        return await message.answer(
            "Пользователь еще не авторизован в системе. "
            "Нажмите или введите команду /login",
            reply_markup=ReplyKeyboardRemove()
        )
    user_db = await UserRepository.get_user(telegram_id=message.from_user.id)
    subscriptions = await UserNewsSubscriptionRepository.get_subscriptions_by_user(user_id=user_db.id)
    await message.answer(
        text="Список каналов",
        reply_markup=ReplyKeyboardRemove()
    )
    text = ""
    for subscription in subscriptions:
        text += (
            f"Ссылка на канал: {subscription.channel.telegram_url}\n"
            f"Период оповещения: {subscription.notifications_period}\n\n"
        )

    await message.answer(
        text=text,
        reply_markup=menu_kbd(),
        disable_web_page_preview=True
    )


@subscription_router.message(Command(commands=['update_period_channel']))
async def update_period_channel(message: types.Message, state: FSMContext) -> Message:
    if not await UserRepository.check_if_user_exists(telegram_id=message.from_user.id):
        return await message.answer(
            "Пользователь еще не авторизован в системе. "
            "Нажмите или введите команду /login",
            reply_markup=ReplyKeyboardRemove()
        )
    return await message.answer("Изменить период оповещения для канала")


@subscription_router.message(Command(commands=['remove_channel']))
async def remove_channel(message: types.Message, state: FSMContext) -> Message:
    if not await UserRepository.check_if_user_exists(telegram_id=message.from_user.id):
        return await message.answer(
            "Пользователь еще не авторизован в системе. "
            "Нажмите или введите команду /login",
            reply_markup=ReplyKeyboardRemove()
        )
    return await message.answer("Удалить канал")
