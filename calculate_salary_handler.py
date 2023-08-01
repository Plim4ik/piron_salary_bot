from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

async def calculate_salary_button(message: types.Message):
    # Здесь должна быть логика расчета зарплаты на основе файла Excel
    await message.reply("Расчет зарплаты выполнен!")

def register_handlers(dp):
    dp.register_message_handler(calculate_salary_button, Text(equals="Рассчитать зарплату"))
