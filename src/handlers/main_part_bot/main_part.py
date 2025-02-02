from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from src.repositories.postgres.user import UserRepository

main_router = Router()


@main_router.message(F.text == "Отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer(
        "Отменено",
        reply_markup=ReplyKeyboardRemove(),
    )


@main_router.message(Command(commands=['login']))
async def login(message: types.Message, ) -> Message:
    await message.answer("Авторизация в системе...")

    if await UserRepository.check_if_user_exists(telegram_id=message.from_user.id):
        return await message.answer("Пользователь уже авторизован в системе")

    _ = await UserRepository.create_user(telegram_id=message.from_user.id)
    return await message.answer("Пользователь успешно авторизирован!")


@main_router.message(Command(commands=['logout']))
async def logout(message: types.Message, ) -> Message:
    await message.answer("Удаление пользователя...")
    try:
        await UserRepository.delete_user(telegram_id=message.from_user.id)
        return await message.answer("Пользователь успешно удален!")
    except Exception as e:
        return await message.answer("Пользователь не найден!")


@main_router.message(Command(commands=['menu']))
async def menu(message: types.Message, ) -> Message:
    if not await UserRepository.check_if_user_exists(telegram_id=message.from_user.id):
        return await message.answer("Пользователь еще не авторизован в системе")

    return await message.answer("Меню", reply_markup=ReplyKeyboardRemove())


@main_router.message(Command(commands=['add_channel']))
async def add_channel(message: types.Message, ) -> Message:
    return await message.answer("Добавить канал")


@main_router.message(Command(commands=['list_channels']))
async def list_channels(message: types.Message, ) -> Message:
    return await message.answer("Список каналов")


@main_router.message(Command(commands=['update_period_channel']))
async def update_period_channel(message: types.Message, ) -> Message:
    return await message.answer("Изменить период оповещения для канала")


@main_router.message(Command(commands=['remove_channel']))
async def remove_channel(message: types.Message, ) -> Message:
    return await message.answer("Удалить канал")
