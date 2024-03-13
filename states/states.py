from aiogram.dispatcher.filters.state import StatesGroup, State


class Register_States(StatesGroup):
    select_lang = State()
    full_name = State()
    phone_number = State()

class Settings_States(StatesGroup):
    setting = State()
    change_full_name = State()
    change_language = State()
    change_phone_number = State()