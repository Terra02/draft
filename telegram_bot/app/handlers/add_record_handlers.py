# app/handlers/add_record_handlers.py
from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.states.add_record_state import AddRecordState
from app.services.content_service import ContentService
from app.services.history_service import HistoryService
from app.keyboards.confirmation_keyboards import get_confirm_keyboard

router = Router()

@router.message(AddRecordState.waiting_for_title)
async def process_title(message: types.Message, state: FSMContext):
    """Обработка введенного названия"""
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("Действие отменено.", reply_markup=types.ReplyKeyboardRemove())
        return
    
    title = message.text.strip()
    await state.update_data(title=title)
    
    # Запрашиваем тип контента
    await message.answer(
        "🎬 Выберите тип контента:",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="🎥 Фильм")],
                [types.KeyboardButton(text="📺 Сериал")],
                [types.KeyboardButton(text="❌ Отменить")]
            ],
            resize_keyboard=True
        )
    )
    await state.set_state(AddRecordState.waiting_for_content_type)

@router.message(AddRecordState.waiting_for_content_type)
async def process_content_type(message: types.Message, state: FSMContext):
    """Обработка типа контента"""
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("Действие отменено.", reply_markup=types.ReplyKeyboardRemove())
        return
    
    content_type_map = {
        "🎥 Фильм": "movie",
        "📺 Сериал": "series"
    }
    
    user_content_type = content_type_map.get(message.text)
    if not user_content_type:
        await message.answer("Пожалуйста, выберите тип контента из предложенных:")
        return
    
    await state.update_data(content_type=user_content_type)
    
    # Получаем данные
    data = await state.get_data()
    title = data['title']
    
    # Ищем контент
    content_service = ContentService()
    search_result = await content_service.search_content(title, user_content_type)
    
    if search_result["found_in_db"]:
        # Нашли в нашей базе
        content = search_result["db_content"]
        await state.update_data(
            content_id=content['id'],
            content_title=content['title']
        )
        
        await message.answer(
            f"✅ Найден в базе: <b>{content['title']}</b>\n"
            f"📝 Теперь оцените от 1 до 10:",
            reply_markup=types.ReplyKeyboardMarkup(
                keyboard=[[types.KeyboardButton(text="❌ Отменить")]],
                resize_keyboard=True
            ),
            parse_mode="HTML"
        )
        await state.set_state(AddRecordState.waiting_for_rating)
        
    elif search_result["found_in_omdb"]:
        # Нашли в OMDB, спрашиваем добавить ли
        await state.update_data(
            omdb_content=search_result["omdb_content"]
        )
        
        # Создаем клавиатуру
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Да, добавить и оценить", callback_data="add_from_omdb")
        builder.button(text="🔄 Искать другой", callback_data="retry_search")
        builder.button(text="❌ Отменить", callback_data="cancel_search")
        
        await message.answer(
            search_result["formatted_text"],
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        
    else:
        # Не нашли нигде
        builder = InlineKeyboardBuilder()
        builder.button(text="🔄 Попробовать снова", callback_data="retry_search")
        builder.button(text="❌ Отменить", callback_data="cancel_search")
        
        await message.answer(
            search_result["formatted_text"],
            reply_markup=builder.as_markup()
        )

@router.callback_query(F.data == "add_from_omdb")
async def add_from_omdb_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработка добавления из OMDB"""
    data = await state.get_data()
    omdb_content = data.get("omdb_content")
    
    if not omdb_content:
        await callback.answer("❌ Данные OMDB не найдены")
        return
    
    # Добавляем контент в нашу базу
    content_service = ContentService()
    added_content = await content_service.add_from_omdb(omdb_content)
    
    if added_content:
        await state.update_data(
            content_id=added_content['id'],
            content_title=added_content['title']
        )
        
        await callback.message.edit_text(
            f"✅ <b>{added_content['title']}</b> добавлен в базу!\n"
            f"📝 Теперь оцените от 1 до 10:",
            parse_mode="HTML"
        )
        
        await state.set_state(AddRecordState.waiting_for_rating)
    else:
        await callback.message.edit_text(
            "❌ Не удалось добавить фильм в базу. Попробуйте позже."
        )
    
    await callback.answer()

@router.callback_query(F.data == "retry_search")
async def retry_search_handler(callback: types.CallbackQuery, state: FSMContext):
    """Повторить поиск"""
    await callback.message.edit_text("Введите название фильма или сериала:")
    await state.set_state(AddRecordState.waiting_for_title)
    await callback.answer()

@router.callback_query(F.data == "cancel_search")
async def cancel_search_handler(callback: types.CallbackQuery, state: FSMContext):
    """Отменить поиск"""
    await state.clear()
    await callback.message.edit_text("❌ Поиск отменен.")
    await callback.answer()

@router.message(AddRecordState.waiting_for_rating)
async def process_rating(message: types.Message, state: FSMContext):
    """Обработка рейтинга"""
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("Действие отменено.", reply_markup=types.ReplyKeyboardRemove())
        return
    
    try:
        rating = float(message.text.strip().replace(',', '.'))
        
        if 1 <= rating <= 10:
            await state.update_data(rating=rating)
            
            await message.answer(
                "📝 Добавьте заметки или комментарии (или отправьте '-' чтобы пропустить):",
                reply_markup=types.ReplyKeyboardMarkup(
                    keyboard=[[types.KeyboardButton(text="❌ Отменить")]],
                    resize_keyboard=True
                )
            )
            await state.set_state(AddRecordState.waiting_for_notes)
        else:
            await message.answer(
                "⚠️ Рейтинг должен быть от 1 до 10.\n"
                "Пожалуйста, введите число от 1 до 10:"
            )
            
    except ValueError:
        await message.answer(
            "⚠️ Пожалуйста, введите число от 1 до 10.\n"
            "Например: 7.5 или 8"
        )

@router.message(AddRecordState.waiting_for_notes)
async def process_notes(message: types.Message, state: FSMContext):
    """Обработка заметок"""
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("Действие отменено.", reply_markup=types.ReplyKeyboardRemove())
        return
    
    notes = message.text.strip()
    if notes == '-':
        notes = None
        notes_text = "Нет заметок"
    else:
        notes_text = notes[:100] + "..." if len(notes) > 100 else notes
    
    await state.update_data(notes=notes)
    
    # Получаем все данные
    data = await state.get_data()
    
    # Определяем тип контента для отображения
    content_type_ru = "фильм" if data.get('content_type') == 'movie' else "сериал"
    title = data.get('content_title', data.get('title', 'Неизвестно'))
    rating = data.get('rating', 'Не указан')
    
    # Формируем подтверждение
    confirmation_text = (
        f"📋 <b>Проверьте данные:</b>\n\n"
        f"🎬 <b>Название:</b> {title}\n"
        f"📺 <b>Тип:</b> {content_type_ru}\n"
        f"⭐ <b>Рейтинг:</b> {rating}/10\n"
        f"📝 <b>Заметки:</b> {notes_text}\n\n"
        f"Всё верно?"
    )
    
    await message.answer(
        confirmation_text,
        reply_markup=get_confirm_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(AddRecordState.waiting_for_content_type)

@router.callback_query(AddRecordState.waiting_for_content_type, F.data == "confirm_yes")
async def confirm_add_record(callback: types.CallbackQuery, state: FSMContext):
    """Подтверждение добавления записи"""
    data = await state.get_data()
    
    history_service = HistoryService()
    
    try:
        # Добавляем запись в историю просмотров
        result = await history_service.add_view_history(
            telegram_id=callback.from_user.id,
            content_id=data['content_id'],
            rating=data.get('rating'),
            notes=data.get('notes')
        )
        
        if result:
            # Получаем информацию о добавленном контенте
            content_service = ContentService()
            content = await content_service.get_content_by_id(data['content_id'])
            content_title = content.get('title', data.get('content_title', 'фильм')) if content else data.get('content_title', 'фильм')
            
            await callback.message.edit_text(
                f"✅ <b>{content_title}</b> успешно добавлен в историю просмотров!\n\n"
                f"📊 <b>Детали:</b>\n"
                f"⭐ Ваша оценка: {data.get('rating', 'Не указана')}/10\n"
                f"📝 Заметки: {data.get('notes', 'Нет')}\n\n"
                f"Запись сохранена с ID: {result.get('id')}",
                parse_mode="HTML"
            )
        else:
            await callback.message.edit_text(
                f"❌ Не удалось добавить фильм в историю.\n"
                f"Попробуйте позже или обратитесь к администратору."
            )
    
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Произошла ошибка при добавлении:\n"
            f"{str(e)[:100]}..."
        )
    
    await state.clear()

@router.callback_query(AddRecordState.waiting_for_content_type, F.data == "confirm_no")
async def cancel_add_record(callback: types.CallbackQuery, state: FSMContext):
    """Отмена добавления записи - возврат к редактированию"""
    # Предлагаем что редактировать
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Изменить рейтинг", callback_data="edit_rating")
    builder.button(text="📝 Изменить заметки", callback_data="edit_notes")
    builder.button(text="🎬 Изменить название", callback_data="edit_title")
    builder.button(text="❌ Отменить всё", callback_data="cancel_all")
    builder.adjust(1)
    
    await callback.message.edit_text(
        "Что вы хотите изменить?",
        reply_markup=builder.as_markup()
    )

@router.callback_query(AddRecordState.waiting_for_content_type, F.data == "edit_rating")
async def edit_rating_handler(callback: types.CallbackQuery, state: FSMContext):
    """Редактирование рейтинга"""
    await callback.message.edit_text(
        "📝 Введите новую оценку от 1 до 10:",
        reply_markup=None
    )
    await state.set_state(AddRecordState.waiting_for_rating)
    await callback.answer()

@router.callback_query(AddRecordState.waiting_for_content_type, F.data == "edit_notes")
async def edit_notes_handler(callback: types.CallbackQuery, state: FSMContext):
    """Редактирование заметок"""
    await callback.message.edit_text(
        "📝 Введите новые заметки (или '-' чтобы пропустить):",
        reply_markup=None
    )
    await state.set_state(AddRecordState.waiting_for_notes)
    await callback.answer()

@router.callback_query(AddRecordState.waiting_for_content_type, F.data == "edit_title")
async def edit_title_handler(callback: types.CallbackQuery, state: FSMContext):
    """Редактирование названия - начинаем заново"""
    await callback.message.edit_text(
        "Введите новое название фильма или сериала:"
    )
    await state.set_state(AddRecordState.waiting_for_title)
    await callback.answer()

@router.callback_query(AddRecordState.waiting_for_content_type, F.data == "cancel_all")
async def cancel_all_handler(callback: types.CallbackQuery, state: FSMContext):
    """Полная отмена"""
    await state.clear()
    await callback.message.edit_text("❌ Добавление фильма отменено.")
    await callback.answer()

# Обработчик команды /cancel в любое время
@router.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    """Отмена текущего процесса по команде /cancel"""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активного процесса для отмены.")
        return
    
    await state.clear()
    await message.answer(
        "❌ Текущее действие отменено.",
        reply_markup=types.ReplyKeyboardRemove()
    )