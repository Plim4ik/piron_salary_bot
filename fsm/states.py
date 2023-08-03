from aiogram.dispatcher.filters.state import State, StatesGroup

class BotStates(StatesGroup):
    WaitingForExcelUpdate = State()
    WaitingForReportCreation = State()


class RegistrationStates(StatesGroup):
    enter_first_name = State()
    enter_last_name = State()
    enter_phone_number = State()
