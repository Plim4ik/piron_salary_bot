import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Command
from bot_handlers import cmd_start, cmd_help, cmd_get_minutes, process_excel_file, cmd_update_excel, button_handler, get_minutes_directly, callback_data 
from config import TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

dp.register_message_handler(cmd_start, Command('start'))
dp.register_callback_query_handler(get_minutes_directly, callback_data.filter(command="get_minutes_directly"))
dp.register_callback_query_handler(button_handler, callback_data.filter())

dp.register_message_handler(process_excel_file, content_types=types.ContentTypes.DOCUMENT)

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
