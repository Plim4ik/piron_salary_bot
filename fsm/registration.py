from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from config import ADMINS, ALLOWED_USERS, OWNERS
from database.models import User
from fsm.states import RegistrationStates


async def register_user(message: Message, state: FSMContext):
    user_id = message.from_user.id
    tg_username = message.from_user.username

    # Проверяем, разрешен ли пользователь
    if user_id not in ADMINS and user_id not in ALLOWED_USERS and user_id not in OWNERS:
        await message.answer("Извините, у вас нет доступа к этому боту.")
        return

    # Проверяем, существует ли пользователь в базе данных
    user = User.get(user_id)
    if user:
        await message.answer("Вы уже зарегистрированы в системе.")
        return

    await message.answer("Добро пожаловать! Давайте начнем регистрацию. Пожалуйста, введите ваше имя.")
    await RegistrationStates.enter_last_name.set()



    await message.answer(" Пожалуйста, введите вашу фамилию.")
    await RegistrationStates.enter_last_name.set()

    await message.answer("Пожалуйста, введите ваш номер телефона.")
    await RegistrationStates.enter_phone_number.set()

    user_data = await state.get_data()
    user = User(
        tg_id=message.from_user.id,
        tg_username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=user_data['last_name'],
        phone_number=user_data['phone_number'],
        status="не на связи",
        minutes=0,
        salary=0,
        employee_type="обычный",
        user_type="сотрудник"
    )
    user.save()

    await message.answer("Регистрация успешно завершена. Добро пожаловать!")
    await state.finish()




