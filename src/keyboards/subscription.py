from aiogram import types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def user_subscriptions_kbd(user_channels) -> ReplyKeyboardMarkup:
    keyboard_builder = ReplyKeyboardBuilder()
    for channel in user_channels:
        keyboard_builder.row(types.KeyboardButton(text=channel))
    keyboard_builder.row(types.KeyboardButton(text="Отмена"))
    return keyboard_builder.as_markup(resize_keyboard=True)
