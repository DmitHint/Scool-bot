import sqlite3
from create_bot import bot
from keyboards import kb_buy_in
from aiogram import types
from datetime import datetime

# Подключение к базе данных и создание таблиц при необходимости
def sql_start():
    global base,cur
    base=sqlite3.connect('data_base/base.db')
    cur=base.cursor()
    if base:
        print('Data base connected OK!')
    cur.execute('CREATE TABLE IF NOT EXISTS materials(row_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, mat TEXT, format TEXT,\
        school_name TEXT, subject TEXT, description TEXT, price TEXT, nickname TEXT, form TEXT, date TEXT)')
    base.commit()
    cur.execute('CREATE TABLE IF NOT EXISTS queue(user_id TEXT PRIMARY KEY, max TEXT, count TEXT)')
    base.commit()
    cur.execute('CREATE TABLE IF NOT EXISTS users(user_id int PRIMARY KEY, nickname TEXT, first_name TEXT, \
        last_name TEXT, school_name TEXT, form TEXT, balance TEXT, subscription TEXT, bought TEXT)')
    base.commit()


# Изменение username в системе, если пользователь обновил его в telegram
async def sql_update_username(user_id,nickname):
    cur.execute(f"UPDATE users SET nickname='{nickname}' WHERE user_id='{user_id}'")
    base.commit()

# Добавление пользователя
async def sql_add_user(state):
    async with state.proxy() as data:
        cur.execute(f"INSERT INTO users(user_id, nickname, school_name, first_name, last_name, form, balance,\
        subscription, bought) VALUES (?,?,?,?,?,?,?,?,'[]')", tuple(data.values())[1:])
        base.commit()

# Добавление материала  
async def sql_add_materials(mat_info):
    cur.execute('INSERT INTO materials(mat, format, school_name, subject, description, price, nickname, form, date)\
        VALUES (?,?,?,?,?,?,?,?,?)',tuple(mat_info.values()))
    base.commit()

# Добавление клиента в очередь  
async def sql_add_line(user_id,max_cnt,count):
    try:
        cur.execute(f"INSERT INTO queue VALUES ({user_id},{max_cnt},{count})")
        base.commit()
    except: base.commit()


# Изменение данных о пользователе в очереди 
async def sql_change_line(user_id):
    cur.execute(f"SELECT * FROM queue WHERE user_id='{user_id}'")
    user_id,max_cnt,count=cur.fetchone()
    cur.execute(f"UPDATE queue SET count='{int(count)+1}' WHERE user_id='{user_id}'")
    base.commit()

# Изменение имени пользователя
async def sql_change_name(user_id, data):
    cur.execute(f"UPDATE users SET first_name='{data[0]}', last_name='{data[1]}' WHERE user_id='{user_id}'")
    base.commit()


# Все ли материалы из очереди отправлены
async def sql_get_count_is_max(user_id):
    cur.execute(f"SELECT * FROM queue WHERE user_id='{user_id}'")
    user_id,max_cnt,count=cur.fetchone()
    if max_cnt==count: return True
    return False

# Удалить пользователя из очереди   
async def sql_delete_line(user_id):
    cur.execute(f"SELECT * FROM queue WHERE user_id='{user_id}'")
    data=cur.fetchone()
    if (data is not None):
        cur.execute(f"DELETE FROM QUEUE WHERE user_id = '{user_id}'")
        base.commit()

# Перевод монет
async def sql_send_coin(message,state):
    user_1_id = message.from_user.id
    user_1_name=await sql_get_unflsfb(user_1_id)
    user_1_name=user_1_name[1]
    async with state.proxy() as data:
        user_2_name = data['user_name']
        amount = data['amount']
    cur.execute(f"SELECT balance FROM users WHERE user_id='{user_1_id}'")
    balance_1 = float(cur.fetchone()[0])
    cur.execute(f"SELECT balance FROM users WHERE nickname='{user_2_name}'")
    balance_2 = float(cur.fetchone()[0])
    balance_1 = round(balance_1-amount,2)
    balance_2 =round(balance_2+amount,2)
    cur.execute(f"""UPDATE users SET balance={balance_1} WHERE user_id='{user_1_id}'""")
    cur.execute(f"""UPDATE users SET balance={balance_2} WHERE nickname='{user_2_name}'""")
    base.commit()
    cur.execute(f"SELECT user_id, balance FROM users WHERE nickname='{user_2_name}'")
    data = cur.fetchone()
    await bot.send_message(data[0], f'Перевод {amount} coin от @{user_1_name}.\nНа вашем счету {data[1]} coin💎')

# Оплата материала при нажатии на кнопку
async def sql_pay(callback,owner,price,item):
    client = callback.message.chat['username']
    cur.execute(f"SELECT balance FROM users WHERE nickname='{client}'")
    balance_client = float(cur.fetchone()[0])
    balance_client = round(balance_client-price,2)
    cur.execute(f"SELECT bought FROM users WHERE nickname='{client}'")
    bought=eval(cur.fetchone()[0])
    bought.append(int(item))
    cur.execute(f"""UPDATE users SET bought='{bought}' WHERE nickname='{client}'""")
    cur.execute(f"""UPDATE users SET balance={balance_client} WHERE nickname='{client}'""")
    base.commit()
    cur.execute(f"SELECT user_id, balance FROM users WHERE nickname='{client}'")
    data=cur.fetchone()
    await callback.answer(f'Перевод {price} coin отправлен.\nНа вашем счету {data[1]} coin💎')
    if owner=='bot': return
    cur.execute(f"SELECT balance FROM users WHERE nickname='{owner}'")
    balance_owner = cur.fetchone()
    if balance_owner is None:
        return
    balance_owner = float(balance_owner[0])
    balance_owner = round(balance_owner+price,2)
    cur.execute(f"""UPDATE users SET balance={balance_owner} WHERE nickname='{owner}'""")
    base.commit()

# Возвращает стоимость материала
async def sql_get_price(row_id):
    cur.execute(f'SELECT price FROM materials WHERE row_id={row_id}')
    return cur.fetchone()[0]

# Удалить материал из предлагаемых для пользователя
async def sql_del_material(callback, row_id):
    cur.execute(f"SELECT bought FROM users WHERE nickname='{callback.message.chat['username']}'")
    bought = eval(cur.fetchone()[0])
    bought.append(int(row_id))
    cur.execute(f"""UPDATE users SET bought='{bought}' WHERE nickname='{callback.message.chat['username']}'""")
    base.commit()

# Отправить материал при оплате
async def sql_show_material(callback,row_id):
    cur.execute(f'SELECT format, nickname, price FROM materials WHERE row_id={row_id}')
    m_format,user_1,price=cur.fetchone()
    price=float(price)
    cur.execute(f'SELECT * FROM materials WHERE row_id={row_id}')
    data=cur.fetchone()
    text=f'Предмет: *{data[4]}*\nОписание: *{data[5]}*\nКласс: *{data[-2]}*\nДата: *{data[-1]}*\n```#{data[0]}```'
    await bot.send_message(callback.message.chat.id,text,parse_mode=types.ParseMode.MARKDOWN)
    if m_format=='Фото':
        media = types.MediaGroup()
        cur.execute(f'SELECT mat FROM materials WHERE row_id={row_id}')
        mat = eval(cur.fetchone()[0])
        for i in range(len(mat)):
            media.attach_photo(types.InputMediaPhoto(mat[i]),)
        await types.ChatActions.upload_photo()
        await bot.send_media_group(callback.message.chat['id'], media=media)
    elif m_format=='Аудио':
        cur.execute(f'SELECT mat FROM materials WHERE row_id={row_id}')
        mat = cur.fetchone()[0]
        await bot.send_voice(callback.message.chat['id'], mat)
    elif m_format=='Текст':
        cur.execute(f'SELECT mat FROM materials WHERE row_id={row_id}')
        mat = cur.fetchone()[0]
        await bot.send_message(callback.message.chat['id'], mat)
    elif m_format=='Файл':
        cur.execute(f'SELECT mat FROM materials WHERE row_id={row_id}')
        mat = cur.fetchone()[0]
        await bot.send_document(callback.message.chat['id'], mat)
    await sql_pay(callback,user_1,price,row_id)
    await bot.delete_message(callback.message.chat['id'], callback.message.message_id)

# Возвращает user_id, nickname, first_name, form, balance
async def sql_get_unflsfb(user):
    cur.execute(f"SELECT user_id,nickname,first_name,last_name, school_name,form,balance FROM users WHERE user_id='{user}'")
    data = cur.fetchone()
    return data

# Отображение подписок пользователя
async def sql_show_subscriptions(message):
    cur.execute(f"SELECT subscription FROM users WHERE user_id='{message.from_user.id}'")
    subs=eval(cur.fetchone()[0])
    if subs:
        end_str='Вы подписаны на обновления '
        for elem in subs:
            end_str+=elem+', '
        return end_str[:-2]
    return 'В ваших подписках нет ни одного класса'

# Проверка на наличие учеников из класса пользователя
async def sql_check_form(message, form):
    school = (await sql_get_unflsfb(message.from_user.id))[4]
    cur.execute(f"SELECT * FROM users WHERE form='{form}' AND school_name='{school}'")
    data=cur.fetchall()
    if not len(data): return False
    else: return True

# Проверка на наличие учеников из класса пользователя
async def sql_check_payee(username):
    cur.execute(f"SELECT * FROM users WHERE nickname = '{username}'")
    data=cur.fetchall()
    if len(data)==0: return False
    else: return True

# Возвращает подписки пользователя
async def sql_get_subscription(message):
    cur.execute(f"SELECT subscription FROM users WHERE user_id='{message.from_user.id}'")
    return eval(cur.fetchone()[0])

# Обновление подписки пользователя
async def sql_update_subscription(subscription,user_id):
    subscription=str(subscription).replace("'",'"')
    cur.execute(f"""UPDATE users SET subscription='{subscription}' WHERE user_id='{user_id}' """)
    base.commit()

# Удаление учетной записи пользователя из системы
async def sql_delete_user(user):
    cur.execute(f"DELETE FROM users WHERE user_id='{user}'")
    base.commit()

# Считывание имеющихся материалов
async def sql_read_materials(message):
    cur.execute(f"SELECT school_name, subscription, bought FROM users WHERE user_id='{message.from_user.id}'")
    data=cur.fetchone()
    school_name, subscription, bought=data[0], eval(data[1]),eval(data[2])
    cur.execute('SELECT * FROM materials')
    data=cur.fetchall()
    # Проверка данных на актуальность и удаление устаревшего
    for ret in data:
        if ret[-3]=='bot':
            continue
        d_material = datetime.strptime(ret[-1], "%d.%m.%Y")
        d_now = datetime.today()
        razn=(d_now-d_material).days
        if razn>=9:
            cur.execute(f"DELETE FROM materials WHERE row_id={ret[0]}")
            base.commit()

    cur.execute('SELECT * FROM materials ORDER BY row_id')
    data=cur.fetchall()
    finish_data=[]
    for ret in data:
        if ( (ret[0] not in bought) and ((ret[-3]=='bot') or \
            ( (ret[-3]!=message.from_user.username) and (ret[3] == school_name) and (ret[-2] in subscription) ) ) ):
            finish_data.append(ret)
    if finish_data:
        for ret in finish_data:
            await bot.send_message(message.from_user.id, f'Предмет: *{ret[4]}*\nОписание: *{ret[5]}*\nФормат: *{ret[2]}*\nЦена: *{ret[6]}*\
            \nКласс: *{ret[-2]}*\nДата: *{ret[-1]}*\n```#{ret[0]}```',  reply_markup=kb_buy_in, parse_mode=types.ParseMode.MARKDOWN)
    else:
        await bot.send_message(message.from_user.id, 'Для вас нет новых материалов')

