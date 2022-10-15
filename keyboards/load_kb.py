from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


photo = KeyboardButton('📸Фото')
audio = KeyboardButton('🔉Аудио')
text = KeyboardButton('📩Текст')
file = KeyboardButton('📁Файл')
cancel = KeyboardButton('❌Отмена')
kb_load=ReplyKeyboardMarkup(resize_keyboard=True).row(photo,audio,text,file).add(cancel)
