from data_base.sql_db import sql_add_user, sql_get_unflsfb
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from handlers import client, message_to_admin
from keyboards import kb_cancel, kb_client, kb_reg
from config import cities, schools
from data_base.sql_db import sql_delete_line


# Проверка города
async def check_city(nameOfCity):
    for city,variants in cities.items():
        for name in variants:
            if nameOfCity.lower() == name:
                return city 
    return False

# Проверка школы 
async def check_school(nameOfSchool, nameOfCity):
    for school,variants in schools[nameOfCity].items():
        for name in variants:
            endName = nameOfSchool.lower()
            for c in ' "№«»':
                endName = endName.replace(c,'')
            endName = endName.lower()
            if endName == name: return school
    return False
class FSMReg(StatesGroup):
    city = State()
    school_name = State()
    first_name = State()
    last_name = State()
    form = State()


# Приветствие
async def welcome(message=types.Message,state=FSMContext):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    data = await sql_get_unflsfb(message.from_user.id)
    if not message.from_user.username: await client.check_user(message)
    elif data is None:
        if '✅Регистрация' in message.text:
            await reg_start(message)
            return
        await message.answer('Приветствую, дорогой пользователь. Предлагаю перейти к регистрации.', reply_markup=kb_reg)
    else:
        if '✅Регистрация' in message.text:
            await message.answer(f'{data[2]}, Вы уже зарегистрированы', reply_markup=kb_client)
        elif message.text == '/start':
            await message.answer(f'Приветствую, {data[2]}', reply_markup=kb_client)

# Выход из состояний (функция срабатывает во всех состояниях)
async def cancel_handler(message: types.Message, state: FSMContext):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if not(await client.check_user(message, state)): return
    current_state = await state.get_state()
    await message.answer('Вас понял👀', reply_markup=kb_client)
    if current_state is None:
        return
    await sql_delete_line(message.from_user.id)
    await state.finish()

# Начало диалога регистрации, узнаем город
async def reg_start(message: types.Message):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    await message.answer('В каком городе вы учитесь?', reply_markup=kb_cancel)
    await FSMReg.city.set()

# Проверка города и запрос школы
async def get_city(message: types.Message, state: FSMContext):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if message.text.isalpha():
        if await check_city(message.text):
            async with state.proxy() as data:
                data['city'] = await check_city(message.text)
                data['user_id'] = message.from_user.id
                data['nickname'] = message.from_user.username
            await message.answer('Как называется ваше учебное заведение?', reply_markup=kb_cancel)
            await FSMReg.next()
        else:
            await message.answer('Такого населеного пункта в моей базе нет.\nПожалуйста, перепроверьте информацию или свяжитесь с админом, используя команду: /mes_admin')
    else:
        await message.answer('Недопустимое значение🚫', reply_markup=kb_cancel)

# Узнаем и проверям школу
async def get_school(message: types.Message, state: FSMContext):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    async with state.proxy() as data:
        if await check_school(message.text, data['city']):
            data['school_name'] = await check_school(message.text, data['city'])
            await message.answer('Напишите ваше имя', reply_markup=kb_cancel)
            await FSMReg.first_name.set()
        else:
            await message.answer('Такого учебного заведения в моей базе нет.\nПожалуйста, перепроверьте информацию или свяжитесь с админом, используя команду: /mes_admin')

# Берем first_name
async def get_first_name(message: types.Message, state: FSMContext):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if message.text.isalpha():
        async with state.proxy() as data:
            data['user_id'] = message.from_user.id
            data['nickname'] = message.from_user.username
            data['first_name'] = message.text
        await message.answer('Напишите вашу фамилию', reply_markup=kb_cancel)
        await FSMReg.next()
    else:
        await message.answer('Недопустимое значение🚫', reply_markup=kb_cancel)

# Берем last_name
async def get_last_name(message: types.Message, state: FSMContext):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if message.text.isalpha():
        async with state.proxy() as data:
            data['last_name'] = message.text
        await message.answer('В каком вы классе? Например, 9А', reply_markup=kb_cancel)
        await FSMReg.next()
    else:
        await message.answer('Недопустимое значение🚫', reply_markup=kb_cancel)

# Берем form и letter, устанавливаем баланс и подписки по умолчанию
async def get_form(message: types.Message, state: FSMContext):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    kirill = ('АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')
    l = ''
    form = ''
    for c in message.text:
        if c.isdigit():
            form += c
        if c.capitalize() in kirill:
            l += c.capitalize()
    if form == '':
        await message.answer('Неправильный номер класса🚫', reply_markup=kb_cancel)
    elif int(form) < 1 or int(form) > 11:
        await message.answer('Неправильный номер класса🚫', reply_markup=kb_cancel)
    elif len(l) != 1:
        await message.answer('Неправильная буква класса🚫', reply_markup=kb_cancel)
    else:
        async with state.proxy() as data:
            data['form'] = form+'-'+l
            data['balance'] = 20.0
            data['subscription'] = (f'["{data["form"]}"]')
            nb = data['balance']
        await message.answer(f'Благодарю за регистрацию и желаю успехов в учебе😉\nВам начислено {nb} coin💎', reply_markup=kb_client)
        await sql_add_user(state)
        await state.finish()
        await client.fhelp(message)


# Регистрация хендлеров
def register_handlers_registration(dp: Dispatcher):
    dp.register_message_handler(message_to_admin.text_start, commands=['mes_admin'], state='*')
    dp.register_message_handler(welcome, commands=['start'])
    dp.register_message_handler(welcome, lambda message: '✅Регистрация' in message.text, state='*')
    dp.register_message_handler(cancel_handler, lambda message: '❌Отмена' in message.text, state='*')
    dp.register_message_handler(get_city, state=FSMReg.city)
    dp.register_message_handler(get_school, state=FSMReg.school_name)
    dp.register_message_handler(get_first_name, state=FSMReg.first_name)
    dp.register_message_handler(get_last_name, state=FSMReg.last_name)
    dp.register_message_handler(get_form, state=FSMReg.form)
