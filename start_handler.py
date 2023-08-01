from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

async def start_command(message: types.Message):
    await message.reply("Привет! Я бот для работы с файлами Excel. Пришли мне файл Excel, чтобы начать.")

def register_handlers(dp):
    dp.register_message_handler(start_command, commands=Command("start"))
