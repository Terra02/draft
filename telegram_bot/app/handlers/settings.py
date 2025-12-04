from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.keyboards.main_menu import get_main_menu_keyboard
from app.utils.text_templates import get_settings_message

router = Router()

@router.message(Command("settings"))
@router.message(F.text == "⚙️ Настройки")
async def cmd_settings(message: types.Message, state: FSMContext):
    """Показать настройки"""
    await state.clear()
    
    text = get_settings_message()
    keyboard = get_main_menu_keyboard()
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")