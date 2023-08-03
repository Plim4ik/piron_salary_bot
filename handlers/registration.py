from aiogram.dispatcher import FSMContext

@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Добро пожаловать! Пожалуйста, введите ваше имя:")
    await Registration.First_name.set()

@dp.message_handler(state=Registration.First_name)
async def process_first_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['first_name'] = message.text

    await message.answer("Отлично! Теперь введите вашу фамилию:")
    await Registration.Last_name.set()


async def save_user(data):
    user = User(
        tg_id=data['tg_id'],
        tg_username=data['tg_username'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone_number=data['phone_number'],
        status="не на связи",
        minutes=0,
        salary=0,
        employee_type="обычный",
        user_type="сотрудник"
    )
    session.add(user)
    session.commit()
