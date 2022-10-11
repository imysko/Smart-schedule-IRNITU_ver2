from telebot import types
from telebot.types import ReplyKeyboardMarkup


def keyboard_start_menu() -> ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    btn1 = types.KeyboardButton('Расписание 🗓')
    btn2 = types.KeyboardButton('Ближайшая пара ⏱')
    btn3 = types.KeyboardButton('Расписание на сегодня 🍏')
    btn4 = types.KeyboardButton('Расписание на завтра 🍎')
    btn5 = types.KeyboardButton('Поиск 🔎')
    btn6 = types.KeyboardButton('Другое ⚡')
    markup.add(btn1, btn2)
    markup.add(btn3)
    markup.add(btn4)
    markup.add(btn5, btn6)
    return markup
