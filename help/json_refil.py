import os
import json
import configparser

# Чтение путей из файла config.conf
config = configparser.ConfigParser()
config.read('config.conf')

excel_folder_path = config.get('Paths', 'excel_folder')
text_file_path = config.get('Paths', 'text_file')
employees_file_path = config.get('Paths', 'employees_file')

# Открываем файл с данными о минутах
with open(text_file_path, 'r') as file:
    file_data = file.readlines()

# Извлекаем данные о минутах из файла
employee_minutes = {}
for line in file_data:
    if ':' not in line:
        continue
    employee, minutes = line.strip().split(': ')
    employee_minutes[employee] = int(minutes.replace(' минут', ''))

# Открываем файл employees.json и загружаем данные
with open(employees_file_path, 'r') as json_file:
    employees_data = json.load(json_file)

# Обновляем или добавляем информацию о минутах для каждого сотрудника
for employee in employees_data['employees']:
    if employee['name'] in employee_minutes:
        employee['minutes'] = employee_minutes[employee['name']]
    else:
        employees_data['employees'].append({
            'name': employee['name'],
            'minutes': employee['minutes'],
            'type': employee['type'],
            'subordinates': employee['subordinates']
        })

# Записываем обновленные данные в employees.json
with open(employees_file_path, 'w') as json_file:
    json.dump(employees_data, json_file, indent=4, ensure_ascii=False)

print("Данные о минутах успешно обновлены в employees.json.")
