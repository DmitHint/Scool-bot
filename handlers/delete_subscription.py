from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from data_base.sql_db import sql_get_subscription, sql_update_subscription
from keyboards import kb_cancel, kb_client
from handlers import client


class FSM_delete_subscription(StatesGroup):
    process = State()

# Начало удаления подписки
async def delete_subscription_start(message: types.Message):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if not(await client.check_user(message)): return
    await message.answer('Напишите, от обновлений какого класса Вы желаете отписаться', reply_markup=kb_cancel)
    await FSM_delete_subscription.process.set()

# Основные операции
async def finish_delete_subscription(message: types.Message, state: FSMContext):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if not(await client.check_user(message)): return
    # Проверка введенного класса
    kirill = ('АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')
    l=''
    form=''
    subscription=await sql_get_subscription(message)
    for c in message.text:
        if c.isdigit():
            form+=c
        if c.capitalize() in kirill:
            l += c.capitalize()
    if form == '':
        await message.answer('Неправильный номер класса🚫', reply_markup=kb_cancel)
    elif int(form) < 1 or int(form)>11:
        await message.answer('Неправильный номер класса🚫', reply_markup=kb_cancel)
    elif len(l)!=1:
        await message.answer('Неправильный буква класса🚫', reply_markup=kb_cancel)
    elif form+'-'+l not in subscription:
        await message.answer('На этот класс вы не подписаны🚫', reply_markup=kb_cancel)
    else:
        subscription.remove(form+'-'+l)
        await sql_update_subscription(subscription,message.from_user.id)
        await message.answer('Вы отписались от обновлений '+form+'-'+l.capitalize()+ ' класса',reply_markup=kb_client)
        await state.finish()

# Регистрация хендлеров
def register_handlers_delete_subscription(dp: Dispatcher):
    dp.register_message_handler(delete_subscription_start, commands=['delete_sub'])
    dp.register_message_handler(finish_delete_subscription, state=FSM_delete_subscription.process)