import os
import subprocess

config_content = '''
[Paths]
excel_folder = {excel_folder}
text_file = {text_file}
employees_file = {employees_file}
source_directory = {source_directory}
backup_directory = {backup_directory}

[Employees]

[Telegram]
token = 5723852582:AAEILOiqro8f0tPz6TbcZvOIG4s0TOAlLUk
'''

current_dir = os.path.dirname(os.path.abspath(__file__))

config_file_path = os.path.join(current_dir, '..', 'config.conf')

excel_folder = os.path.join(os.getcwd(), 'Excel')
text_file = os.path.join(current_dir, '..', 'Minutes', 'temp.txt')  # Updated path to temp.txt
employees_file = os.path.join(os.getcwd(), 'employees.json')

source_directory = os.path.join(current_dir, '..') 
backup_directory = os.path.join(os.getcwd(), 'backup')

minutes_calc = os.path.join(current_dir, 'minutes_calc.py')


with open(config_file_path, 'w') as config_file:
    config_file.write(config_content.format(
        excel_folder=excel_folder,
        text_file=text_file,
        employees_file=employees_file,
        source_directory=source_directory,
        backup_directory=backup_directory

    ))

subprocess.Popen(['python3', minutes_calc])

print("Файл config.conf создан успешно в текущей папке.")
