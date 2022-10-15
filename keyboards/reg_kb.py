from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

b1 = KeyboardButton('✅Регистрация')

kb_reg = ReplyKeyboardMarkup(resize_keyboard=True).add(b1)
