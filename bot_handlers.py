import os
from datetime import datetime, timedelta
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from minutes_calc import calculate_minutes
from config import EXCEL_FOLDER, ADMINS, ALLOWED_USERS
from keyboards import get_start_keyboard, get_back_keyboard, get_force_update_keyboard, get_minutes_keyboard

async def button_handler(callback_query: types.CallbackQuery, callback_data: dict):
    # Получаем команду из callback_data
    command = callback_data["command"]

    if command == "help":
        await cmd_help(callback_query.message)
    elif command == "update_excel":
        await cmd_update_excel(callback_query.message)
    elif command == "get_minutes":
        await cmd_get_minutes(callback_query.message)
    elif command == "start":
        await callback_query.message.edit_text('Привет! Я бот, который поможет вам подсчитать суммарное количество минут на основе вашего файла Excel.', reply_markup=get_start_keyboard(callback_query.from_user.id))
    elif command == "force_update_excel":
        await cmd_force_update_excel(callback_query)
    elif command == "confirm_force_update":
        # Запрашиваем новый файл Excel у пользователя
        await callback_query.message.answer('Пожалуйста, отправьте новый файл Excel.')

    # Завершаем обратный вызов, чтобы кнопка перестала "грузиться"
    await callback_query.answer()

async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in ALLOWED_USERS and user_id not in ADMINS:
        await message.answer("Извините, у вас нет доступа к этому боту.")
        return
    await message.bot.send_message(message.chat.id, 'Привет! Я бот, который поможет вам подсчитать суммарное количество минут на основе вашего файла Excel.', reply_markup=get_start_keyboard(user_id))

async def cmd_force_update_excel(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text('Вы уверены, что хотите принудительно обновить файл Excel?', reply_markup=get_force_update_keyboard())

async def cmd_help(message: types.Message):
    await message.bot.send_message(message.chat.id, 'Отправьте мне файл Excel, и я подсчитаю суммарное количество минут.', reply_markup=get_back_keyboard())

async def cmd_update_excel(message: types.Message):
    if message.from_user.id not in ADMINS:
        await message.answer("Извините, у вас нет доступа к этому функционалу.")
        return

    # Проверяем наличие файлов Excel в папке
    excel_files = [f for f in os.listdir(EXCEL_FOLDER) if f.endswith('.xlsx')]
    if not excel_files:
        await message.bot.send_message(message.chat.id, 'Пожалуйста, отправьте мне файл Excel.', reply_markup=get_back_keyboard())
        return

    # Сортируем файлы по дате изменения и берем самый свежий
    excel_files.sort(key=lambda x: os.path.getmtime(os.path.join(EXCEL_FOLDER, x)), reverse=True)
    latest_file = excel_files[0]
    modification_time = datetime.fromtimestamp(os.path.getmtime(os.path.join(EXCEL_FOLDER, latest_file)))

    # Если файл старше одного дня, предлагаем пользователю принудительное обновление
    if datetime.now() - modification_time > timedelta(days=1):
        await message.bot.send_message(message.chat.id, 'Ваш файл Excel старше одного дня. Вы хотите обновить его?', reply_markup=get_force_update_keyboard())
    else:
        await message.bot.send_message(message.chat.id, 'Ваш файл Excel свежий. Вы хотите его обновить?', reply_markup=get_force_update_keyboard())

async def cmd_get_minutes(message: types.Message):
    # Проверяем наличие файлов Excel в папке
    excel_files = [f for f in os.listdir(EXCEL_FOLDER) if f.endswith('.xlsx')]
    if not excel_files:
        await message.bot.send_message(message.chat.id, 'Пожалуйста, сначала отправьте мне файл Excel.', reply_markup=get_back_keyboard())
        return

    # Сортируем файлы по дате изменения и берем самый свежий
    excel_files.sort(key=lambda x: os.path.getmtime(os.path.join(EXCEL_FOLDER, x)), reverse=True)
    latest_file = excel_files[0]
    modification_time = datetime.fromtimestamp(os.path.getmtime(os.path.join(EXCEL_FOLDER, latest_file)))

    # Если файл старше одного дня, предлагаем пользователю обновить его
    if datetime.now() - modification_time > timedelta(days=1):
        await message.bot.send_message(message.chat.id, 'Ваш файл Excel старше одного дня. Вы хотите обновить его прежде чем получить минуты?', reply_markup=get_minutes_keyboard())
    else:
        await message.bot.send_message(message.chat.id, 'Ваш файл Excel свежий. Вы хотите его обновить перед подсчетом минут?', reply_markup=get_minutes_keyboard())

async def get_minutes_directly(callback_query: types.CallbackQuery):
    # Выполняем расчет минут
    excel_files = [f for f in os.listdir(EXCEL_FOLDER) if f.endswith('.xlsx')]
    excel_files.sort(key=lambda x: os.path.getmtime(os.path.join(EXCEL_FOLDER, x)), reverse=True)
    latest_file = excel_files[0]
    minutes_summary = calculate_minutes(os.path.join(EXCEL_FOLDER, latest_file))
    await callback_query.message.edit_text(minutes_summary, reply_markup=get_back_keyboard())

async def process_excel_file(message: types.Message):
    if message.from_user.id not in ADMINS:
        await message.answer("Извините, у вас нет доступа к этому функционалу.")
        return
    if message.document:
        await message.document.download(destination_dir=EXCEL_FOLDER)
        await message.bot.send_message(message.chat.id, 'Файл успешно сохранен. Вы можете использовать команду /get_minutes для подсчета минут.', reply_markup=get_back_keyboard())
    else:
        await message.bot.send_message(message.chat.id, 'Пожалуйста, отправьте мне файл Excel.', reply_markup=get_back_keyboard())
