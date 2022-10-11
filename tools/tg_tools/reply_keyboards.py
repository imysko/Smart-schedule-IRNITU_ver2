from telebot import types
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove


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


def keyboard_extra() -> ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    btn1 = types.KeyboardButton('Помощь')
    btn2 = types.KeyboardButton('Напоминание 📣')
    btn3 = types.KeyboardButton('Основное меню')
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    return markup


def keyboard_choose_schedule() -> ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    btn1 = types.KeyboardButton('На текущую неделю')
    btn2 = types.KeyboardButton('На следующую неделю')
    btn3 = types.KeyboardButton('Экзамены')
    btn4 = types.KeyboardButton('Основное меню')
    markup.add(btn1, btn2)
    markup.add(btn3)
    markup.add(btn4)
    return markup


def keyboard_near_lesson() -> ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    btn1 = types.KeyboardButton('Текущая')
    btn2 = types.KeyboardButton('Следующая')
    btn3 = types.KeyboardButton('Основное меню')
    markup.add(btn1, btn2)
    markup.add(btn3)
    return markup


def keyboard_search_goal() -> ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    btn1 = types.KeyboardButton('Группы и преподаватели')
    btn2 = types.KeyboardButton('Аудитории')
    btn3 = types.KeyboardButton('Основное меню')
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    return markup


def make_keyboard_empty() -> ReplyKeyboardRemove:
    markup = types.ReplyKeyboardRemove()
    return markup
