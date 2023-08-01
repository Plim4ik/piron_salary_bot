import os
import openpyxl
from math import ceil
from datetime import datetime
import configparser
import aiogram
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Чтение конфигурационного файла
config = configparser.ConfigParser()
config.read('config.conf')

# Получение пути к папке "Excel" из конфигурационного файла
excel_folder = config.get('Paths', 'excel_folder')

# Получение списка всех файлов в папке "Excel"
files = os.listdir(excel_folder)

# Фильтрация файлов по расширению ".xlsx"
xlsx_files = [file for file in files if file.endswith(".xlsx")]

# Проверка, есть ли файлы в списке
if not xlsx_files:
    print("Нет файлов формата .xlsx в папке 'Excel'")
    exit()

# Сортировка файлов по дате изменения в обратном порядке
xlsx_files.sort(key=lambda x: os.path.getmtime(os.path.join(excel_folder, x)), reverse=True)

# Выбор самого свежего файла
latest_file = xlsx_files[0]

# Формирование полного пути к выбранному файлу
file_path = os.path.join(excel_folder, latest_file)

# Открытие файла
workbook = openpyxl.load_workbook(file_path)

# Выбираем активный лист
sheet = workbook.active

# Получаем дату и время начала и конца отчетного периода из файла
start_date_cell = sheet['B6'].value
end_date_cell = sheet['B7'].value

# Конвертируем дату начала и конца отчетного периода в datetime объекты
start_date = datetime.strptime(start_date_cell, "%m/%d/%Y %H:%M")
end_date = datetime.strptime(end_date_cell, "%m/%d/%Y %H:%M")

# Форматируем дату начала и конца отчетного периода в требуемый формат
start_date_str = start_date.strftime("%m.%d.%Y %H:%M")
end_date_str = end_date.strftime("%m.%d.%Y %H:%M")

# Создаем словарь для хранения суммарного количества округленных минут для каждого сотрудника
summary = {}

# Итерируемся по строкам в таблице, начиная со второй строки (первая строка содержит заголовки)
for row in sheet.iter_rows(min_row=2, values_only=True):
    call_type = row[0]  # Тип звонка
    duration = row[10]  # Длительность звонка
    employee = row[2]  # Сотрудник
    waiting_time = row[9]  # Время ожидания

    # Пропускаем значения типа звонка "неотвеченный"
    if call_type == 'неотвеченный':
        # Продолжаем только если сотрудник "Сообщение о нерабочем времени"
        if employee != 'Сообщение о нерабочем времени':
            continue

    # Пропускаем пустые значения и строку с заголовками
    if duration is None or employee is None or duration == 'Длительность':
        continue

    # Разбиваем значение длительности на часы, минуты и секунды
    hours, minutes, seconds = map(int, str(duration).split(':'))

    # Если секунды больше 2, добавляем еще одну минуту
    if seconds > 2:
        minutes += 1

    # Округляем количество минут в большую сторону
    minutes = ceil(minutes)

    # Добавляем количество округленных минут к суммарному значению для данного сотрудника
    if employee in summary:
        summary[employee] += minutes
    else:
        summary[employee] = minutes

    # Обрабатываем случай "Сообщение о нерабочем времени"
    if employee == 'Сообщение о нерабочем времени':
        # Пропускаем пустые значения времени ожидания
        if waiting_time is None or waiting_time == 'Ожидание':
            continue

        # Разбиваем значение времени ожидания на часы, минуты и секунды
        waiting_hours, waiting_minutes, waiting_seconds = map(int, str(waiting_time).split(':'))

        # Если секунды больше 2, добавляем еще одну минуту
        if waiting_seconds > 2:
            waiting_minutes += 1

        # Округляем количество минут в большую сторону
        waiting_minutes = ceil(waiting_minutes)

        # Добавляем количество округленных минут к суммарному значению для сотрудника "Сообщение о нерабочем времени"
        if 'Сообщение о нерабочем времени' in summary:
            summary['Сообщение о нерабочем времени'] += waiting_minutes
        else:
            summary['Сообщение о нерабочем времени'] = waiting_minutes

# Вычисляем общее количество минут
total_minutes = sum(summary.values())

# Добавляем общее количество минут в словарь для сотрудника "Итого"
summary['Итого'] = total_minutes

# Закрываем файл
workbook.close()

# Создаем имя файла с указанием даты и времени отчетного периода
file_name = f"Минуты с {start_date_str} по {end_date_str}.txt"
file_path = os.path.join("Minutes", file_name)

# Открываем файл для записи результата
with open(file_path, 'w') as file:
    # Записываем результат в файл
    file.write(f"Дата создания отчета: {datetime.now().strftime('%d.%m.%Y')}\n\n")
    file.write("Звонки: Внешние\n")
    file.write(f"С: {start_date_str}\n")
    file.write(f"По: {end_date_str}\n\n")
    file.write("Сотрудник\tКоличество минут\n")
    for employee, minutes in summary.items():
        file.write(f"{employee}\t{minutes}\n")

# Создание бота и хранилища состояний
bot = Bot(token=config.get('Telegram', 'token'))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("Привет! Я бот для отправки файла с минутами в Telegram. "
                         "Чтобы получить файл, введи команду /get_minutes.")

# Запуск бота
if __name__ == '__main__':
    # Запуск бота с использованием long polling
    aiogram.executor.start_polling(dp, skip_updates=True)
