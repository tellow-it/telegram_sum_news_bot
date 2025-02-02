from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

start_router = Router()


@start_router.message(F.text == "Отмена")
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


@start_router.message(Command(commands=['start']))
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
