from aiogram.fsm.state import StatesGroup, State


class AddNewsChannelForm(StatesGroup):
    GET_NEWS_CHANNEL = State()
    GET_NOTIFICATION_PERIOD = State()


class UpdateNotificationPeriodForm(StatesGroup):
    GET_NEWS_CHANNEL = State()
    GET_NEW_NOTIFICATION_PERIOD = State()


class RemoveNewsChannelForm(StatesGroup):
    GET_NEWS_CHANNEL = State()
