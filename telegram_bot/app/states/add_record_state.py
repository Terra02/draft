from aiogram.fsm.state import State, StatesGroup

class AddRecordState(StatesGroup):
    waiting_for_title = State()
    waiting_for_content_type = State()
    waiting_for_rating = State()
    waiting_for_notes = State()