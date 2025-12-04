from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from app.states.search_state import SearchState
from app.keyboards.search_keyboards import get_search_results_keyboard

from app.utils.text_templates import get_search_results_message
import logging
import sys
import traceback


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("search"))
@router.message(F.text == "🔍 Поиск")
async def cmd_search(message: types.Message, state: FSMContext):
    """Начать процесс поиска"""
    await state.set_state(SearchState.waiting_for_query)
    await message.answer(
        "🔍 Введите название фильма или сериала для поиска:",
        reply_markup=types.ReplyKeyboardRemove()
    )

##переписать код чтобы он не перебирал endpoints

@router.message(SearchState.waiting_for_query)
async def process_search_query(message: types.Message, state: FSMContext):
    """Обработать поисковый запрос"""
    
    query = message.text.strip()
    logger.info(f"🔍 Поиск: '{query}'")
    
    search_message = await message.answer("🔍 Ищем...")
    
    try:
        from app.services.api_client import api_client
        
        # Сначала проверьте доступность API
        logger.info("🔌 Проверяем доступность API...")
        health_response = await api_client.get("/health")  # или /docs, /openapi.json
        
        if health_response:
            logger.info(f"✅ API доступен. Ответ: {health_response}")
        else:
            logger.error("❌ API недоступен")
            
        # Попробуйте разные endpoint
        endpoints = [
            "/api/v1/content/search",
            "/api/content/search",
            "/content/search", 
            "/search",
            "/contents",
            "/content",
            "/api/search",
            "/api/v1/search"
        ]
        
        response = None
        working_endpoint = None
        
        for endpoint in endpoints:
            logger.info(f"🔄 Пробуем endpoint: {endpoint}")
            params = {"query": query, "limit": 5}
            response = await api_client.get(endpoint, params=params)
            if response:
                logger.info(f"✅ Endpoint найден: {endpoint}")
                working_endpoint = endpoint
                break
            else:
                logger.info(f"❌ Endpoint {endpoint} не найден или ошибка")
        
        if not response:
            # Если API не отвечает, используем заглушку для тестирования
            logger.warning("⚠️ API не отвечает, используем тестовые данные")
            
            # Тестовые данные
            response = {
                "results": [
                    {
                        "id": 1,
                        "title": "Тестовый фильм 1",
                        "release_year": "2023",
                        "content_type": "movie",
                        "description": "Описание тестового фильма"
                    },
                    {
                        "id": 2,
                        "title": "Тестовый сериал 1",
                        "release_year": "2024",
                        "content_type": "series",
                        "description": "Описание тестового сериала"
                    },
                    {
                        "id": 3,
                        "title": "Тестовый фильм 2",
                        "release_year": "2022",
                        "content_type": "movie",
                        "description": "Второй тестовый фильм"
                    },
                    {
                        "id": 4,
                        "title": "Тестовый сериал 2",
                        "release_year": "2021",
                        "content_type": "series",
                        "description": "Второй тестовый сериал"
                    },
                    {
                        "id": 5,
                        "title": "Тестовый фильм 3",
                        "release_year": "2020",
                        "content_type": "movie",
                        "description": "Третий тестовый фильм"
                    }
                ],
                "total": 5,
                "page": 1,
                "size": 5
            }
            
            logger.info(f"📊 Используем тестовые данные: {len(response['results'])} результатов")
        
        # Извлекаем результаты из ответа
        if isinstance(response, dict):
            results = response.get("results", [])
            total = response.get("total", len(results))
        else:
            # Если ответ не словарь, а просто список
            results = response if isinstance(response, list) else []
            total = len(results)
        
        logger.info(f"✅ Найдено результатов: {len(results)}")
        
        if len(results) == 0:
            await search_message.edit_text("❌ Ничего не найдено.")
            await state.clear()
            return
        
        # Сохраняем результаты
        await state.update_data(
            search_results=results, 
            current_page=0,
            search_query=query,
            total_results=total,
            working_endpoint=working_endpoint
        )
        
        # Формируем сообщение и клавиатуру
        try:
            text = get_search_results_message(results, 0)
            keyboard = get_search_results_keyboard(results, 0)
            
            await search_message.edit_text(text, reply_markup=keyboard)
            await state.set_state(SearchState.waiting_for_selection)
            logger.info(f"✅ Поиск завершен, показано {len(results[:5])} результатов на странице")
        except Exception as e:
            logger.error(f"❌ Ошибка при формировании сообщения: {e}")
            
            # Простой fallback вывод
            simple_text = f"🔍 Найдено {len(results)} результатов по запросу: {query}\n\n"
            for i, item in enumerate(results[:5], 1):
                title = item.get('title', 'Без названия')
                year = item.get('release_year', item.get('year', 'N/A'))
                simple_text += f"{i}. {title} ({year})\n"
            
            await search_message.edit_text(simple_text)
            await state.set_state(SearchState.waiting_for_selection)
        
    except ImportError as e:
        logger.error(f"❌ Ошибка импорта: {e}")
        await search_message.edit_text("❌ Ошибка в настройке системы. Обратитесь к администратору.")
        await state.clear()
    except Exception as e:
        logger.error(f"💥 Ошибка при поиске: {e}", exc_info=True)
        await search_message.edit_text("❌ Произошла ошибка при поиске. Попробуйте позже.")
        await state.clear()

@router.callback_query(F.data.startswith("search_page_"))
async def change_search_page(callback: types.CallbackQuery, state: FSMContext):
    """Смена страницы результатов поиска"""
    data = await state.get_data()
    results = data.get("search_results", [])
    current_page = int(callback.data.split("_")[2])
    query = data.get("search_query", "")
    
    # Исправленный вызов функций - только 2 аргумента
    text = get_search_results_message(results, current_page)
    keyboard = get_search_results_keyboard(results, current_page)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.update_data(current_page=current_page)
    await callback.answer()


@router.callback_query(F.data == "new_search")
async def new_search(callback: types.CallbackQuery, state: FSMContext):
    """Новый поиск"""
    await state.set_state(SearchState.waiting_for_query)
    await callback.message.edit_text("🔍 Введите название фильма или сериала для поиска:")
    await callback.answer()