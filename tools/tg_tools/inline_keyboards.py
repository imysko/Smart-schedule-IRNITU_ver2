import json

from keyboa import Keyboa
from telebot import types
from telebot.types import InlineKeyboardMarkup

user_role = [
    {'Я студент': '{"registration": "student"}'},
    {'Я преподователь': '{"registration": "teacher"}'}
]
reminders = [
    {'Настройки': '{"reminders": "settings"}'},
    {'Свернуть': '{"reminders": "close"}'}
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


def keyboard_reminders() -> InlineKeyboardMarkup:
    return Keyboa(items=reminders)()


def keyboard_set_notifications(time: int = 0):
    markup = types.InlineKeyboardMarkup()
    data_del = json.dumps({"del_notifications": time})
    if time != 0:
        text_check = f'{time} мин'
    else:
        text_check = 'off'
    data_add = json.dumps({"add_notifications": time})
    markup.add(types.InlineKeyboardButton(text='-', callback_data=data_del),
               types.InlineKeyboardButton(text=text_check, callback_data='None'),
               types.InlineKeyboardButton(text='+', callback_data=data_add))

    data_save = json.dumps({"save_notifications": time})
    markup.add(types.InlineKeyboardButton(text='Сохранить', callback_data=data_save))
    return markup
