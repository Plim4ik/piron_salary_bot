import logging
from aiogram import Bot, Dispatcher, executor, types
from bot_handlers import cmd_start, process_excel_file, get_minutes_directly, button_handler
from keyboards import callback_data
from config import TOKEN, ALLOWED_USERS, GROUP_CHAT_ID
from datetime import datetime, timedelta
import asyncio

logging.basicConfig(level=logging.INFO)

async def check_and_remind_users():
    while True:
        # Получаем текущее время
        now = datetime.now()
        start_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
        end_time = now.replace(hour=8, minute=30, second=0, microsecond=0)

        # Если текущее время входит в интервал, начинаем проверку
        if start_time <= now <= end_time:
            group_history = await bot.get_chat_history(GROUP_CHAT_ID, limit=100) # Получаем последние 100 сообщений из группового чата
            messages_from_allowed_users = [msg for msg in group_history['messages'] if msg['from_user']['id'] in ALLOWED_USERS]

            for user_id in ALLOWED_USERS:
                last_message_from_user = next((msg for msg in messages_from_allowed_users if msg['from_user']['id'] == user_id), None)
                
                if last_message_from_user:
                    last_message_time = datetime.fromtimestamp(last_message_from_user['date'])
                else:
                    last_message_time = None

                if last_message_time is None or last_message_time < start_time:
                    user_mention = f"[{user_id}](tg://user?id={user_id})"
                    reminder_text = f"Привет, {user_mention}, вы не написали свое расписание, пожалуйста, укажите"
                    await bot.send_message(user_id, reminder_text)
                    await bot.send_message(GROUP_CHAT_ID, reminder_text)

        await asyncio.sleep(60)  # Пауза в 60 секунд перед следующей проверкой

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Обработчики
dp.register_message_handler(cmd_start, Command('start'))
dp.register_callback_query_handler(get_minutes_directly, callback_data.filter(command="get_minutes_directly"))
dp.register_callback_query_handler(button_handler, callback_data.filter())
dp.register_message_handler(process_excel_file, content_types=types.ContentTypes.DOCUMENT)

if __name__ == '__main__':
    from aiogram import executor

    # Запуск задачи напоминания
    dp.loop.create_task(check_and_remind_users())

    executor.start_polling(dp, skip_updates=True)
