from aiogram.fsm.state import State, StatesGroup

class EditRecordState(StatesGroup):
    waiting_for_rating = State()
    waiting_for_notes = State()