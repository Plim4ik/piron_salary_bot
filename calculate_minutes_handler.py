from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

async def calculate_minutes_button(message: types.Message):
    # Здесь должна быть логика расчета минут на основе файла Excel
    await message.reply("Расчет минут выполнен!")

def register_handlers(dp):
    dp.register_message_handler(calculate_minutes_button, Text(equals="Рассчитать минуты"))
