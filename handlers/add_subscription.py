from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from data_base.sql_db import sql_get_subscription, sql_update_subscription, sql_check_form
from keyboards import kb_cancel, kb_client
from handlers import client


class FSM_new_subscription(StatesGroup):
    process = State()
   

# Начало добавление подписки
async def add_subscription_start(message: types.Message):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if not(await client.check_user(message)): return
    await message.answer('Напишите, на обновления какого класса Вы желаете подписаться', reply_markup=kb_cancel)
    await FSM_new_subscription.process.set()

# Основные операции
async def finish_add_subscription(message: types.Message, state: FSMContext):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if not(await client.check_user(message)): return
    # Проверка введенного класса
    kirill = ('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
    l=''
    form=''
    subscription=await sql_get_subscription(message)
    for c in message.text:
        if c.isdigit():
            form+=c
        if c.lower() in kirill:
            l += c.lower()
    if form == '':
        await message.answer('Неправильный номер класса🚫', reply_markup=kb_cancel)
    elif int(form) < 1 or int(form)>11:
        await message.answer('Неправильный номер класса🚫', reply_markup=kb_cancel)
    elif len(l)!=1:
        await message.answer('Неправильная буква класса🚫', reply_markup=kb_cancel)
    else:
        # Формирование названия класса
        form=form+'-'+l.capitalize()
        if form in subscription:
            await message.answer('На обновления этого класса вы уже подписаны🚫', reply_markup=kb_cancel)
            return    
        subscription.append(form)
        await sql_update_subscription(subscription,message.from_user.id)
        await message.answer('Вы подписались на обновления '+form+' класса',reply_markup=kb_client)
        # Предложение поделиться ботом
        if not(await sql_check_form(message, form)):
            await message.answer(f'К сожалению, учеников этого класса, зарегистрированных в *Scool*, нет. Поделитесь с ними ботом🙃',\
                reply_markup=kb_client,parse_mode=types.ParseMode.MARKDOWN)
                
        await state.finish()

# Регистрация хендлеров
def register_handlers_add_subscription(dp: Dispatcher):
    dp.register_message_handler(add_subscription_start, commands=['new_sub'])
    dp.register_message_handler(finish_add_subscription, state=FSM_new_subscription.process)