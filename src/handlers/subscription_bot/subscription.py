from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from core.logger import logger
from src.keyboards.subscription import user_subscriptions_kbd
from src.keyboards.utils import cancel_kbd, menu_kbd

from src.repositories.postgres.channel import ChannelRepository
from src.repositories.postgres.user import UserRepository
from src.handlers.subscription_bot.steps import (
    AddNewsChannelForm,
    UpdateNotificationPeriodForm,
    RemoveNewsChannelForm
)
from src.repositories.postgres.user_news_subscription import (
    UserNewsSubscriptionRepository
)
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
async def get_news_channel_for_adding_channel(
        message: types.Message,
        state: FSMContext
) -> Message:
    if not await UserRepository.check_if_user_exists(telegram_id=message.from_user.id):
        return await message.answer(
            "Пользователь еще не авторизован в системе. "
            "Нажмите или введите команду /login",
            reply_markup=ReplyKeyboardRemove()
        )
    await message.answer(f"Вы указали ссылку на канал: {message.text}!")
    if message.text and is_valid_url(message.text):  # check input val
        await RedisRepository.set_value(
            key=f'add_channel:news_channel:user_id:{message.from_user.id}',
            value=message.text
        )
        await message.answer(
            text="Введите период оповещения в минутах для данного канала",
            reply_markup=cancel_kbd()
        )
        await state.set_state(AddNewsChannelForm.GET_NOTIFICATION_PERIOD)
    else:
        await message.answer(
            text="Введена некорректна ссылка, попробуйте еще раз",
            reply_markup=cancel_kbd()
        )
        await state.set_state(AddNewsChannelForm.GET_NEWS_CHANNEL)


@subscription_router.message(AddNewsChannelForm.GET_NOTIFICATION_PERIOD)
async def get_notification_period_for_adding_channel(
        message: types.Message,
        state: FSMContext
) -> Message:
    if not await UserRepository.check_if_user_exists(telegram_id=message.from_user.id):
        return await message.answer(
            "Пользователь еще не авторизован в системе. "
            "Нажмите или введите команду /login",
            reply_markup=ReplyKeyboardRemove()
        )
    await message.answer(f"Вы ввели период: {message.text}!")
    if message.text and str(message.text).isnumeric():  # check input val
        await RedisRepository.set_value(
            key=f'add_channel:period:user_id:{message.from_user.id}',
            value=int(message.text)
        )
        name_news_channel_from_user = await RedisRepository.get_value(
            f'add_channel:news_channel:user_id:{message.from_user.id}')
        notification_period_from_user = await RedisRepository.get_value(
            f'add_channel:period:user_id:{message.from_user.id}')
        try:
            user_db = await UserRepository.get_user(telegram_id=message.from_user.id)
            news_channel = await ChannelRepository.create_channel(
                telegram_url=name_news_channel_from_user
            )
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
            return await message.answer(
                text="Не удалось добавить подписку! "
                     "Возможного для данного пользователя "
                     "подписка на этот канал уже добавлена",
                reply_markup=menu_kbd()
            )
    else:
        await message.answer(
            text="Введен некорректный период, попробуйте еще раз",
            reply_markup=cancel_kbd()
        )
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
    subscriptions = await UserNewsSubscriptionRepository.get_subscriptions_by_user(
        user_id=user_db.id
    )
    if not subscriptions:
        await state.clear()
        return await message.answer(
            text="У вас нет подписок",
            reply_markup=menu_kbd()
        )

    await message.answer(
        text="Список каналов",
        reply_markup=ReplyKeyboardRemove()
    )
    text = ""
    for subscription in subscriptions:
        join_status_text = "Да" if subscription.channel.join_status else "Нет"
        text += (
            f"Ссылка на канал: {subscription.channel.telegram_url}\n"
            f"Период оповещения в минутах: {subscription.notifications_period}\n"
            f"Канал доступен для сбора: {join_status_text}\n"
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
            text="Пользователь еще не авторизован в системе. "
                 "Нажмите или введите команду /login",
            reply_markup=ReplyKeyboardRemove()
        )
    user_db = await UserRepository.get_user(telegram_id=message.from_user.id)
    subscriptions = await UserNewsSubscriptionRepository.get_subscriptions_by_user(
        user_id=user_db.id
    )

    if not subscriptions:
        await state.clear()
        return await message.answer(
            text="У вас нет подписок",
            reply_markup=menu_kbd()
        )
    user_channels = [sub.channel.telegram_url for sub in subscriptions]
    await message.answer(
        text="Выберете новостной канал",
        reply_markup=user_subscriptions_kbd(user_channels)
    )
    await state.set_state(UpdateNotificationPeriodForm.GET_NEWS_CHANNEL)


@subscription_router.message(UpdateNotificationPeriodForm.GET_NEWS_CHANNEL)
async def get_news_channel_for_update(message: types.Message, state: FSMContext):
    if not await UserRepository.check_if_user_exists(telegram_id=message.from_user.id):
        return await message.answer(
            text="Пользователь еще не авторизован в системе. "
                 "Нажмите или введите команду /login",
            reply_markup=ReplyKeyboardRemove()
        )
    user_db = await UserRepository.get_user(telegram_id=message.from_user.id)
    subscriptions = await UserNewsSubscriptionRepository.get_subscriptions_by_user(
        user_id=user_db.id
    )
    if not subscriptions:
        await state.clear()
        return await message.answer(
            text="У вас нет подписок",
            reply_markup=menu_kbd()
        )

    user_channels = {sub.channel.telegram_url: sub.channel_id for sub in subscriptions}

    if message.text not in user_channels.keys():
        await message.answer(
            text="Данного канала нет в ваших подписках, попробуйте снова",
            reply_markup=user_subscriptions_kbd(list(user_channels.keys()))
        )
        return await state.set_state(UpdateNotificationPeriodForm.GET_NEWS_CHANNEL)

    selected_channel_id = user_channels[message.text]

    await RedisRepository.set_value(
        key=f'update_period:channel_id:user_id:{message.from_user.id}',
        value=selected_channel_id
    )
    await message.answer(
        text="Введите новый период оповещения в минутах",
        reply_markup=cancel_kbd()
    )
    await state.set_state(UpdateNotificationPeriodForm.GET_NEW_NOTIFICATION_PERIOD)


@subscription_router.message(UpdateNotificationPeriodForm.GET_NEW_NOTIFICATION_PERIOD)
async def get_period_for_update(message: types.Message, state: FSMContext) -> Message:
    if not await UserRepository.check_if_user_exists(telegram_id=message.from_user.id):
        return await message.answer(
            text="Пользователь еще не авторизован в системе. "
                 "Нажмите или введите команду /login",
            reply_markup=ReplyKeyboardRemove()
        )
    user_db = await UserRepository.get_user(telegram_id=message.from_user.id)
    subscriptions = await UserNewsSubscriptionRepository.get_subscriptions_by_user(
        user_id=user_db.id
    )
    if not subscriptions:
        await state.clear()
        return await message.answer(
            text="У вас нет подписок",
            reply_markup=menu_kbd()
        )

    if not str(message.text).isnumeric():
        await message.answer(
            text="Необходимо ввести число, попробуйте снова",
            reply_markup=cancel_kbd()
        )
        await state.set_state(UpdateNotificationPeriodForm.GET_NEW_NOTIFICATION_PERIOD)

    selected_channel_id = await RedisRepository.get_value(
        key=f'update_period:channel_id:user_id:{message.from_user.id}'
    )
    try:
        await UserNewsSubscriptionRepository.update_subscription(
            user_id=user_db.id,
            channel_id=int(selected_channel_id),
            new_notification_period=int(message.text)
        )
        await state.clear()
        return await message.answer(
            text="Период оповещения для подписки успешно изменен!",
            reply_markup=menu_kbd()
        )
    except Exception as e:
        logger.error(e)
        await state.clear()
        return await message.answer(
            text="Не удалось обновить подписку",
            reply_markup=menu_kbd()
        )


@subscription_router.message(Command(commands=['remove_channel']))
async def remove_channel(message: types.Message, state: FSMContext) -> Message:
    if not await UserRepository.check_if_user_exists(telegram_id=message.from_user.id):
        return await message.answer(
            "Пользователь еще не авторизован в системе. "
            "Нажмите или введите команду /login",
            reply_markup=ReplyKeyboardRemove()
        )
    user_db = await UserRepository.get_user(telegram_id=message.from_user.id)
    subscriptions = await UserNewsSubscriptionRepository.get_subscriptions_by_user(
        user_id=user_db.id
    )

    if not subscriptions:
        await state.clear()
        return await message.answer(
            text="У вас нет подписок",
            reply_markup=menu_kbd()
        )
    user_channels = [sub.channel.telegram_url for sub in subscriptions]
    await message.answer(
        text="Выберете новостной канал",
        reply_markup=user_subscriptions_kbd(user_channels)
    )
    await state.set_state(RemoveNewsChannelForm.GET_NEWS_CHANNEL)


@subscription_router.message(RemoveNewsChannelForm.GET_NEWS_CHANNEL)
async def get_news_channel_for_remove(message: types.Message, state: FSMContext):
    if not await UserRepository.check_if_user_exists(telegram_id=message.from_user.id):
        return await message.answer(
            text="Пользователь еще не авторизован в системе. "
                 "Нажмите или введите команду /login",
            reply_markup=ReplyKeyboardRemove()
        )
    user_db = await UserRepository.get_user(telegram_id=message.from_user.id)
    subscriptions = await UserNewsSubscriptionRepository.get_subscriptions_by_user(
        user_id=user_db.id
    )
    if not subscriptions:
        await state.clear()
        return await message.answer(
            text="У вас нет подписок",
            reply_markup=menu_kbd()
        )

    user_channels = {sub.channel.telegram_url: sub.channel_id for sub in subscriptions}

    if message.text not in user_channels:
        await message.answer(
            text="Данного канала нет в ваших подписках, попробуйте снова",
            reply_markup=user_subscriptions_kbd(list(user_channels.keys()))
        )
        return await state.set_state(RemoveNewsChannelForm.GET_NEWS_CHANNEL)

    selected_channel_id = user_channels[message.text]

    await RedisRepository.set_value(
        key=f'remove_channel:channel_id:user_id:{message.from_user.id}',
        value=selected_channel_id
    )
    try:
        await UserNewsSubscriptionRepository.delete_subscription(
            user_id=user_db.id,
            channel_id=selected_channel_id
        )
        await state.clear()
        return await message.answer(
            text="Подписка успешно удалена!",
            reply_markup=menu_kbd()
        )
    except Exception as err:
        logger.error(str(err))
        await state.clear()
        return await message.answer(
            text="Возникла ошибка при удалении подписки",
            reply_markup=menu_kbd()
        )
