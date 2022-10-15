from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

b1 = KeyboardButton('🔔Новенькое')
b2 = KeyboardButton('🚀Загрузить')
b3 = KeyboardButton('💸Перевод')
b4 = KeyboardButton('👤Профиль')
# b5 = KeyboardButton('🗺️Отправить, где я', request_location=True)

kb_client = ReplyKeyboardMarkup(resize_keyboard=True).add(b1).insert(b2).add(b3).insert(b4)
