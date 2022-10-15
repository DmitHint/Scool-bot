from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from data_base import sql_db as sq
from keyboards import kb_cancel, kb_client, kb_load
from datetime import date
from handlers import client


class FSMLoad(StatesGroup):
    choice = State()
    count = State()
    load= State()
    name = State()
    description = State()
    price = State()

# Начало диалога загрузки
async def load_start(message: types.Message):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if not(await client.check_user(message)): return
    await message.answer('Выберите, что желаете отправить', reply_markup=kb_load)
    await FSMLoad.choice.set()

# Сохранение выбора формата
async def load_choice(message: types.Message, state: FSMContext):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if not(await client.check_user(message)): return
    if message.text == '📸Фото':
        async with state.proxy() as data:
            data['format'] = 'Фото'
        await message.answer('Введите количество фотографий', reply_markup=kb_cancel)
        await FSMLoad.count.set()
    elif message.text == '🔉Аудио':
        async with state.proxy() as data:
            data['format'] = 'Аудио'
        await sq.sql_add_line(message.from_user.id,1,0)
        await message.answer('Оставьте аудио сообщение', reply_markup=kb_cancel)
        await FSMLoad.load.set()
    elif message.text == '📩Текст':
        async with state.proxy() as data:
            data['format'] = 'Текст'
        await sq.sql_add_line(message.from_user.id,1,0)
        await message.answer('Напишите свое послание', reply_markup=kb_cancel)
        await FSMLoad.load.set()
    elif message.text == '📁Файл':
        async with state.proxy() as data:
            data['format'] = 'Файл'
        await sq.sql_add_line(message.from_user.id,1,0)
        await message.answer('Загрузите файл', reply_markup=kb_cancel)
        await FSMLoad.load.set()
    else:
        await message.answer('Неправильное значение🚫',reply_markup=kb_cancel)

# Сохранение количества фотографий
async def load_count(message: types.Message, state: FSMContext):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if not(await client.check_user(message)): return
    try:
        if message.content_type != 'text':
            raise ValueError
        max_cnt = int(message.text)
        if not (1 <= max_cnt <= 10):
            await message.answer('Неправильное значение🚫', reply_markup=kb_cancel)
        else:
            await sq.sql_add_line(message.from_user.id,max_cnt,0)
            async with state.proxy() as data:
                data['mat'] = []
            await message.answer('Загрузите фотографии', reply_markup=kb_cancel)
            await FSMLoad.load.set()
    except (TypeError, ValueError):
        await message.answer('Напишите число🚫', reply_markup=kb_cancel)

# Сохранение ссылок на материалы для базы данных
async def load_material(message: types.Message, state: FSMContext):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if not(await client.check_user(message)): return
    async with state.proxy() as data:
        if data['format']=='Фото':
            if message.content_type == 'photo':
                data['mat'].append(message.photo[-1].file_id)
                await sq.sql_change_line(message.from_user.id)
            else:
                await message.answer('Неправильный формат🚫', reply_markup=kb_cancel)
        elif data['format']=='Аудио':
            if message.content_type == 'voice':
                data['mat']=message.voice.file_id
                await sq.sql_change_line(message.from_user.id)
            else:
                await message.answer('Неправильный формат🚫', reply_markup=kb_cancel)
        elif data['format']=='Текст':
            if message.content_type == 'text':
                data['mat']=message.text
                await sq.sql_change_line(message.from_user.id)
            else:
                await message.answer('Неправильный формат🚫', reply_markup=kb_cancel)
        elif data['format']=='Файл':
            if message.content_type == 'document':
                data['mat']=message.document.file_id
                await sq.sql_change_line(message.from_user.id)
            else:
                await message.answer('Неправильный формат🚫', reply_markup=kb_cancel) 
    if await sq.sql_get_count_is_max(message.from_user.id):
        await FSMLoad.name.set()
        await message.answer('Введите название предмета', reply_markup=kb_cancel)
      
# Сохранение названия предмета
async def load_name(message: types.Message, state: FSMContext):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if not(await client.check_user(message)): return
    async with state.proxy() as data:
        data['subject'] = message.text
        data['mat'] = str(data['mat'])
    await FSMLoad.description.set()
    await message.answer('Введите описание')

# Сохранение описания
async def load_description(message: types.Message, state: FSMContext):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if not(await client.check_user(message)): return
    async with state.proxy() as data:
        data['description'] = message.text
    await FSMLoad.price.set()
    await message.answer('Теперь укажите цену', reply_markup=kb_cancel)

# Сохранение цены и формирование данных для загрузки в базу данных
async def load_price(message: types.Message, state: FSMContext):
    await client.write_history(message.from_user.id, message.from_user.username, message.text)
    if not(await client.check_user(message)): return
    async with state.proxy() as data:
        try:
            message.text=message.text.replace(',','.')
            price = float(message.text)
            if price<0.01:
                await message.answer('Минимальное значение составляет 0.01 coin🚫', reply_markup=kb_cancel)
                return
            if len(str(price).split('.')[1])>2:
                await message.answer('Введите число, у которого количество знаков после точки меньше трех🚫', reply_markup=kb_cancel)
                return
            data['price'] = float(message.text)
            user = await sq.sql_get_unflsfb(message.from_user.id)
            data['nickname'] = user[1]
            data['school_name'] = str(user[4])
            data['form'] = str(user[5])
            cur_date=str(date.today()).split('-')[::-1]
            cur_date='.'.join(cur_date)
            mat_info = {'mat': data['mat'], 'format': data['format'],'school_name': data['school_name'], 'subject': data['subject'],
                        'description': data['description'], 'price': data['price'], 'nickname': data['nickname'],
                        'form': data['form'],  'date': cur_date, }
            await sq.sql_add_materials(mat_info)
            await sq.sql_delete_line(message.from_user.id)
            await state.finish()
            await message.answer('Материал успешно добавлен', reply_markup=kb_client)
        except  ValueError:
            await message.answer('Напишите число🚫', reply_markup=kb_cancel)

# Регистрация хендлеров
def register_handlers_load(dp: Dispatcher):
    dp.register_message_handler(load_start, lambda message: '🚀Загрузить' in message.text)
    dp.register_message_handler(load_choice, state=FSMLoad.choice)
    dp.register_message_handler(load_count, state=FSMLoad.count)
    dp.register_message_handler(load_count, content_types=['photo'], state=FSMLoad.count)
    dp.register_message_handler(load_material, content_types=['photo','voice','text','document'], state=FSMLoad.load)
    dp.register_message_handler(load_name, state=FSMLoad.name)
    dp.register_message_handler(load_description, state=FSMLoad.description)
    dp.register_message_handler(load_price, state=FSMLoad.price)
