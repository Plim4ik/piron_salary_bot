import sqlite3

# Путь к файлу базы данных SQLite
db_path = "/Users/plimrecords/Documents/GitHub/piron_salary_bot/data/salary_bot.db"

# Создание соединения с базой данных
conn = sqlite3.connect(db_path)

# Создание курсора для выполнения SQL-запросов
cursor = conn.cursor()

# SQL-запрос для создания таблицы пользователей
create_users_table_query = """
CREATE TABLE IF NOT EXISTS users (
    tg_id INTEGER PRIMARY KEY,
    tg_username TEXT,
    first_name TEXT,
    last_name TEXT,
    phone_number TEXT,
    status TEXT,
    minutes REAL,
    salary REAL,
    employee_type TEXT CHECK(employee_type IN('подчиненный','менеджер')),
    user_type TEXT CHECK(user_type IN ('сотрудник', 'админ', 'владелец'))
);
"""

# Выполнение запроса
cursor.execute(create_users_table_query)

# Закрытие соединения с базой данных
conn.close()
