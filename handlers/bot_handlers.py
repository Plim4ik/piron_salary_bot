import os
from datetime import datetime, timedelta
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from help.minutes_calc import calculate_minutes
from help.report_processing import handle_report_file
from config import EXCEL_FOLDER, ADMINS, ALLOWED_USERS, EXCEL_OUTPUT_FOLDER, EXCEL_REPORTS_FOLDER, OWNERS
from help.report_processing import process_excel_file 
from keyboards.keyboards import get_start_keyboard, get_back_keyboard, get_force_update_keyboard, get_minutes_keyboard

async def button_handler(callback_query: types.CallbackQuery, callback_data: dict):
    user_id = callback_query.from_user.id
    # Получаем команду из callback_data
    command = callback_data["command"]

    if command == "help":
        await cmd_help(callback_query.message)
    elif command == "update_excel":
        await cmd_update_excel(callback_query.message, user_id)
    if command == "get_minutes":
        await cmd_get_minutes(callback_query.message, user_id)
    elif command == "start":
        await callback_query.message.edit_text('Привет! Я бот, который поможет вам подсчитать суммарное количество минут на основе вашего файла Excel.', reply_markup=get_start_keyboard(callback_query.from_user.id))
    elif command == "force_update_excel":
        await cmd_force_update_excel(callback_query)
    elif command == "confirm_force_update":
        await callback_query.message.bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text='Пожалуйста, отправьте новый файл Excel.', reply_markup=get_back_keyboard())
    elif command == "create_report":
        await cmd_create_report(callback_query.message, user_id)


    # Завершаем обратный вызов, чтобы кнопка перестала "грузиться"
    await callback_query.answer()

async def cmd_create_report(message: types.Message, user_id: int):
    if user_id not in ADMINS:
        await message.answer("Извините, у вас нет доступа к этой функции.")
        return

    # await message.answer("Пожалуйста, загрузите файл .xlsx для формирования отчета.")
    await message.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Пожалуйста, загрузите файл .xlsx для формирования отчета.", reply_markup=get_back_keyboard())


async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in ALLOWED_USERS and user_id not in ADMINS:
        await message.answer("Извините, у вас нет доступа к этому боту.")
        return
    await message.bot.send_message(message.chat.id, 'Привет! Я бот, который поможет вам подсчитать суммарное количество минут на основе вашего файла Excel.', reply_markup=get_start_keyboard(user_id))

async def cmd_force_update_excel(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text('Вы уверены, что хотите принудительно обновить файл Excel?', reply_markup=get_force_update_keyboard())

async def cmd_help(message: types.Message):
   await message.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Отправьте мне файл Excel, и я подсчитаю суммарное количество минут.', reply_markup=get_back_keyboard())

async def cmd_update_excel(message: types.Message, user_id: int): 
    # Проверяем доступ пользователя по user_id
    if user_id not in ADMINS:
        await message.answer("Извините, у вас нет доступа к этому функционалу.")
        return

    # Проверяем наличие файлов Excel в папке
    excel_files = [f for f in os.listdir(EXCEL_FOLDER) if f.endswith('.xlsx')]
    if not excel_files:
        await message.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id-1, text='Пожалуйста, отправьте мне файл Excel.', reply_markup=get_back_keyboard())
        return

    # Сортируем файлы по дате изменения и берем самый свежий
    excel_files.sort(key=lambda x: os.path.getmtime(os.path.join(EXCEL_FOLDER, x)), reverse=True)
    latest_file = excel_files[0]
    modification_time = datetime.fromtimestamp(os.path.getmtime(os.path.join(EXCEL_FOLDER, latest_file)))

    # Если файл старше одного дня, предлагаем пользователю принудительное обновление
    if datetime.now() - modification_time > timedelta(days=1):
        await message.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Ваш файл Excel старше одного дня. Вы хотите обновить его?', reply_markup=get_force_update_keyboard())
        # await message.bot.send_message(message.chat.id, 'Ваш файл Excel старше одного дня. Вы хотите обновить его?', reply_markup=get_force_update_keyboard())
    else:
        await message.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Ваш файл Excel свежий. Вы хотите его обновить?', reply_markup=get_force_update_keyboard())
        # await message.bot.send_message(message.chat.id, 'Ваш файл Excel свежий. Вы хотите его обновить?', reply_markup=get_force_update_keyboard())

async def cmd_get_minutes(message: types.Message, user_id: int):
    # Проверяем наличие файлов Excel в папке
    excel_files = [f for f in os.listdir(EXCEL_FOLDER) if f.endswith('.xlsx')]
    if not excel_files:
        await message.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Пожалуйста, отправьте мне файл Excel.', reply_markup=get_back_keyboard(user_id))
        return

    # Сортируем файлы по дате изменения и берем самый свежий
    excel_files.sort(key=lambda x: os.path.getmtime(os.path.join(EXCEL_FOLDER, x)), reverse=True)
    latest_file = excel_files[0]
    modification_time = datetime.fromtimestamp(os.path.getmtime(os.path.join(EXCEL_FOLDER, latest_file)))

    # Если файл старше одного дня, предлагаем пользователю обновить его
    if datetime.now() - modification_time > timedelta(days=1):
        await message.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Ваш файл Excel старше одного дня. Вы хотите обновить его прежде чем получить минуты?', reply_markup=get_minutes_keyboard(user_id))
        # await message.bot.send_message(message.chat.id, 'Ваш файл Excel старше одного дня. Вы хотите обновить его прежде чем получить минуты?', reply_markup=get_minutes_keyboard())
    else:
        await message.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Ваш файл Excel свежий. Вы хотите его обновить перед подсчетом минут?', reply_markup=get_minutes_keyboard(user_id))
        # await message.bot.send_message(message.chat.id, 'Ваш файл Excel свежий. Вы хотите его обновить перед подсчетом минут?', reply_markup=get_minutes_keyboard())

async def get_minutes_directly(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    # Выполняем расчет минут
    excel_files = [f for f in os.listdir(EXCEL_FOLDER) if f.endswith('.xlsx')]
    excel_files.sort(key=lambda x: os.path.getmtime(os.path.join(EXCEL_FOLDER, x)), reverse=True)
    latest_file = excel_files[0]
    minutes_summary = calculate_minutes(os.path.join(EXCEL_FOLDER, latest_file))

    if user_id in ADMINS:
        # Администраторы получают полный отчет
        await callback_query.message.edit_text(minutes_summary, reply_markup=get_back_keyboard())
    else:
        # Обычные пользователи получают только свои минуты
        user_name = ALLOWED_USERS.get(user_id)
        if user_name:
            user_minutes_line = next((line for line in minutes_summary.split('\n') if user_name in line), None)
            if user_minutes_line:
                await callback_query.message.edit_text(user_minutes_line, reply_markup=get_back_keyboard())
            else:
                await callback_query.message.edit_text(f"Минуты для пользователя {user_name} не найдены.", reply_markup=get_back_keyboard())
        else:
            await callback_query.message.edit_text("Извините, у вас нет доступа к этому боту.", reply_markup=get_back_keyboard())


async def process_excel_file(message: types.Message):
    if message.from_user.id not in ADMINS:
        await message.answer("Извините, у вас нет доступа к этому функционалу.")
        return
    if message.document:
        # Путь к файлу внутри папки EXCEL_FOLDER с оригинальным именем файла
        file_name = message.document.file_name
        file_path = os.path.join(EXCEL_FOLDER, file_name)
        await message.document.download(destination_file=file_path)  # Использование destination_file вместо destination
        
        # Удаляем сообщение с файлом из чата
        await message.delete()

        # Отправляем сообщение о том, что файл успешно сохранен, и указываем название файла
        success_text = f'Файл успешно сохранен. \nНазвание файла: {file_name}.'
        await message.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id-1, text=success_text, reply_markup=get_back_keyboard())
    else:
        await message.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id-1, text='Пожалуйста, отправьте мне файл Excel.', reply_markup=get_back_keyboard())


# Обновляем функцию cmd_create_report
async def cmd_create_report(message: types.Message, user_id: int):
    if user_id not in ADMINS:
        await message.answer("Извините, у вас нет доступа к этой функции.")
        return

    await message.answer("Пожалуйста, загрузите файл .xlsx для формирования отчета.", reply_markup=get_back_keyboard())

# Добавляем новую функцию для обработки файла отчета
async def process_report_file(message: types.Message):
    user_id = message.from_user.id
    if user_id not in ADMINS or message.document is None:
        return

    # Сохраняем файл
    file_path = os.path.join(EXCEL_REPORTS_FOLDER, message.document.file_name)
    await message.document.download(destination_file=file_path)

    # Отправляем сообщение о том, что файл загружен
    # await message.answer("Файл успешно загружен. Пожалуйста, подождите...")
    await message.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Файл успешно загружен. Пожалуйста, подождите...", reply_markup=get_back_keyboard())
    # Обрабатываем файл
    output_file_path = handle_report_file(file_path)  # Измените на handle_report_file
    
    await message.delete()

    # Отправляем файл пользователю
    with open(output_file_path, "rb") as file:
        await message.answer_document(file, caption="Отчет сформирован.")