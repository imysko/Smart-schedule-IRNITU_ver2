from keyboa import Keyboa
from telebot import types
from telebot.types import InlineKeyboardMarkup, ReplyKeyboardMarkup

user_role = [
    {'Я студент': '{"registration": "student"}'},
    {'Я преподователь': '{"registration": "teacher"}'}
]


def keyboard_back(callback: str) -> InlineKeyboardMarkup:
    return Keyboa(items={'<': '{"' + callback + '": "back"}'})()


def keyboard_user_role() -> InlineKeyboardMarkup:
    return Keyboa(items=user_role)()


def keyboard_institutes(institutes: list) -> InlineKeyboardMarkup:
    return Keyboa.combine(keyboards=(Keyboa(items=institutes)(), keyboard_back('registration')))


def keyboard_courses(courses: list) -> InlineKeyboardMarkup:
    return Keyboa.combine(keyboards=(Keyboa(items=courses)(), keyboard_back('institute')))


def keyboard_groups(groups: list) -> InlineKeyboardMarkup:
    return Keyboa.combine(keyboards=(Keyboa(items=groups)(), keyboard_back('course')))


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
