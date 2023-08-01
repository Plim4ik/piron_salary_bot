import os
from datetime import datetime, timedelta
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from minutes_calc import calculate_minutes
from config import EXCEL_FOLDER
from aiogram.utils.callback_data import CallbackData

# Создаем объект CallbackData
callback_data = CallbackData("action", "command")

def get_back_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Назад", callback_data=callback_data.new(command="start")))
    return keyboard

async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Помощь", callback_data=callback_data.new(command="help")))
    keyboard.add(InlineKeyboardButton("Обновить Excel", callback_data=callback_data.new(command="update_excel")))
    keyboard.add(InlineKeyboardButton("Получить минуты", callback_data=callback_data.new(command="get_minutes")))
    await message.answer('Привет! Я бот, который поможет вам подсчитать суммарное количество минут на основе вашего файла Excel.', reply_markup=keyboard)

async def cmd_force_update_excel(message: types.Message):
    keyboard = get_back_keyboard()
    keyboard.add(InlineKeyboardButton("Да", callback_data=callback_data.new(command="confirm_force_update")))
    keyboard.add(InlineKeyboardButton("Нет", callback_data=callback_data.new(command="start")))
    await message.answer('Вы уверены, что хотите принудительно обновить файл Excel?', reply_markup=keyboard)

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
        await cmd_start(callback_query.message)
    elif command == "force_update_excel":
        await cmd_force_update_excel(callback_query.message)
    elif command == "confirm_force_update":
        # Запрашиваем новый файл Excel у пользователя
        await callback_query.message.answer('Пожалуйста, отправьте новый файл Excel.')

    # Завершаем обратный вызов, чтобы кнопка перестала "грузиться"
    await callback_query.answer()

async def cmd_help(message: types.Message):
    await message.answer('Отправьте мне файл Excel, и я подсчитаю суммарное количество минут.', reply_markup=get_back_keyboard())

async def cmd_update_excel(message: types.Message):
    # Проверяем наличие файлов Excel в папке
    excel_files = [f for f in os.listdir(EXCEL_FOLDER) if f.endswith('.xlsx')]
    if not excel_files:
        await message.answer('Пожалуйста, отправьте мне файл Excel.', reply_markup=get_back_keyboard())
        return

    # Сортируем файлы по дате изменения и берем самый свежий
    excel_files.sort(key=lambda x: os.path.getmtime(os.path.join(EXCEL_FOLDER, x)), reverse=True)
    latest_file = excel_files[0]
    modification_time = datetime.fromtimestamp(os.path.getmtime(os.path.join(EXCEL_FOLDER, latest_file)))

    # Если файл старше одного дня, предлагаем пользователю принудительное обновление
    keyboard = get_back_keyboard()
    keyboard.add(InlineKeyboardButton("Да", callback_data=callback_data.new(command="force_update_excel")))
    keyboard.add(InlineKeyboardButton("Нет", callback_data=callback_data.new(command="start")))
    if datetime.now() - modification_time > timedelta(days=1):
        await message.answer('Ваш файл Excel старше одного дня. Вы хотите обновить его?', reply_markup=keyboard)
    else:
        await message.answer('Ваш файл Excel свежий. Вы хотите его обновить?', reply_markup=keyboard)

async def cmd_get_minutes(message: types.Message):
    # Проверяем наличие файлов Excel в папке
    excel_files = [f for f in os.listdir(EXCEL_FOLDER) if f.endswith('.xlsx')]
    if not excel_files:
        await message.answer('Пожалуйста, сначала отправьте мне файл Excel.', reply_markup=get_back_keyboard())
        return

    # Сортируем файлы по дате изменения и берем самый свежий
    excel_files.sort(key=lambda x: os.path.getmtime(os.path.join(EXCEL_FOLDER, x)), reverse=True)
    latest_file = excel_files[0]
    modification_time = datetime.fromtimestamp(os.path.getmtime(os.path.join(EXCEL_FOLDER, latest_file)))

    # Если файл старше одного дня, предлагаем пользователю обновить его
    keyboard = get_back_keyboard()
    keyboard.add(InlineKeyboardButton("Да", callback_data=callback_data.new(command="force_update_excel")))
    keyboard.add(InlineKeyboardButton("Нет", callback_data=callback_data.new(command="get_minutes_directly")))
    if datetime.now() - modification_time > timedelta(days=1):
        await message.answer('Ваш файл Excel старше одного дня. Вы хотите обновить его прежде чем получить минуты?', reply_markup=keyboard)
    else:
        await message.answer('Ваш файл Excel свежий. Вы хотите его обновить перед подсчетом минут?', reply_markup=keyboard)

async def get_minutes_directly(callback_query: types.CallbackQuery):
    # Выполняем расчет минут
    excel_files = [f for f in os.listdir(EXCEL_FOLDER) if f.endswith('.xlsx')]
    excel_files.sort(key=lambda x: os.path.getmtime(os.path.join(EXCEL_FOLDER, x)), reverse=True)
    latest_file = excel_files[0]
    minutes_summary = calculate_minutes(os.path.join(EXCEL_FOLDER, latest_file))
    await callback_query.message.answer(minutes_summary, reply_markup=get_back_keyboard())

async def process_excel_file(message: types.Message):
    if message.document:
        await message.document.download(destination_dir=EXCEL_FOLDER)
        await message.answer('Файл успешно сохранен. Вы можете использовать команду /get_minutes для подсчета минут.', reply_markup=get_back_keyboard())
    else:
        await message.answer('Пожалуйста, отправьте мне файл Excel.', reply_markup=get_back_keyboard())
