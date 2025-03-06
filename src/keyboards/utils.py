from aiogram import types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def menu_kbd() -> ReplyKeyboardMarkup:
    keyboard_builder = ReplyKeyboardBuilder()
    menu = [
        "Список каналов",
        "Добавить канал",
        "Изменить период оповещения для канала",
        "Удалить канал"
    ]
    for folder in menu:
        keyboard_builder.row(types.KeyboardButton(text=folder))
    keyboard_builder.row(types.KeyboardButton(text="Отмена"))
    return keyboard_builder.as_markup(resize_keyboard=True)


def cancel_kbd() -> ReplyKeyboardMarkup:
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.row(types.KeyboardButton(text="Отмена"))
    return keyboard_builder.as_markup(resize_keyboard=True)
