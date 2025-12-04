from aiogram.fsm.state import State, StatesGroup

class SearchState(StatesGroup):
    waiting_for_query = State()
    waiting_for_selection = State()