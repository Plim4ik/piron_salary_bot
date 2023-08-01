import json

# Загрузка данных о сотрудниках из файла
def load_employees():
    with open('employees.json') as f:
        data = json.load(f)
        return data['employees']
    
# Сохранение данных о сотрудниках в файл
def save_employees(employees):
    with open('employees.json', 'w') as f:
        json.dump({'employees': employees}, f, ensure_ascii=False, indent=4)

# Добавление сотрудника
def add_employee(name, minutes, employee_type, subordinates=None):
    employees = load_employees()
    employee = {
        'name': name,
        'minutes': minutes,
        'type': employee_type
    }
    if subordinates:
        employee['subordinates'] = subordinates
    employees.append(employee)
    save_employees(employees)

# Обновление данных о сотруднике
def update_employee(name, minutes, employee_type, subordinates=None):
    employees = load_employees()
    for employee in employees:
        if employee['name'] == name:
            employee['minutes'] = minutes
            employee['type'] = employee_type
            if subordinates:
                employee['subordinates'] = subordinates
            break
    save_employees(employees)

# Удаление сотрудника
def remove_employee(name):
    employees = load_employees()
    employees = [e for e in employees if e['name'] != name]
    save_employees(employees)

def update_list(self):
    self.employee_list.delete(0, END)
    self.employees = load_employees()
    for employee in self.employees:
        self.employee_list.insert(END, f"{employee['name']}: {employee['minutes']} minutes")
