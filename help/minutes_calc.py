import os
import openpyxl
from math import ceil
from datetime import datetime

def calculate_minutes(file_path):
    # Открытие файла
    workbook = openpyxl.load_workbook(file_path)

    # Выбираем активный лист
    sheet = workbook.active

    # Получаем дату и время начала и конца отчетного периода из файла
    start_date_cell = sheet['B6'].value
    end_date_cell = sheet['B7'].value

    # # Конвертируем дату начала и конца отчетного периода в datetime объекты
    # start_date = datetime.strptime(start_date_cell, "%m/%d/%Y %H:%M")
    # end_date = datetime.strptime(end_date_cell, "%m/%d/%Y %H:%M")

    # # Форматируем дату начала и конца отчетного периода в требуемый формат
    # start_date_str = start_date.strftime("%m.%d.%Y %H:%M")
    # end_date_str = end_date.strftime("%m.%d.%Y %H:%M")

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

    return '\n'.join([f'{employee}: {minutes} минут' for employee, minutes in summary.items()])
