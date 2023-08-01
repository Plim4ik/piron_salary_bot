import json
from help.manage_employees import load_employees

# Подсчет зарплаты подчиненного и менеджера
def calc_subordinate_salary(minutes):
    return (minutes // 150 + 1) * 1000

# Подсчет зарплаты менеджера
def calc_manager_salary(minutes, subordinates_minutes):
    return calc_subordinate_salary(minutes) + subordinates_minutes * 5

# Поиск сотрудника по имени
def get_employee_by_name(name, employees):
    for employee in employees:
        if employee['name'] == name:
            return employee
    return None

# Подсчет зарплаты всех сотрудников
def calculate_salaries():
    employees = load_employees()
    for employee in employees:
        if employee['type'] == 'подчиненный':
            employee['salary'] = calc_subordinate_salary(employee['minutes'])
        elif employee['type'] == 'менеджер':
            total_subordinates_minutes = sum([get_employee_by_name(subordinate, employees)['minutes'] for subordinate in employee.get('subordinates', []) if get_employee_by_name(subordinate, employees) is not None])
            employee['salary'] = calc_manager_salary(employee['minutes'], total_subordinates_minutes)
    return employees

# Подсчет общего счета


