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
main_menu = [
    {'Основное меню': '{"search": "main"}'}
]


def keyboard_main_menu() -> InlineKeyboardMarkup:
    return Keyboa(items=main_menu)()


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


def keyboard_set_notifications(time: int = 0) -> InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    data_del = json.dumps({"decrease_reminder_time": time})
    if time != 0:
        text_check = f'{time} мин'
    else:
        text_check = 'off'
    data_add = json.dumps({"increase_reminder_time": time})
    markup.add(types.InlineKeyboardButton(text='-', callback_data=data_del),
               types.InlineKeyboardButton(text=text_check, callback_data='None'),
               types.InlineKeyboardButton(text='+', callback_data=data_add))

    data_save = json.dumps({"save_reminder_time": time})
    markup.add(types.InlineKeyboardButton(text='Сохранить', callback_data=data_save))
    return markup


def keyboard_with_possible_teachers(teachers: list) -> InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    for teacher in teachers:
        data = json.dumps({'teacher_id': teacher['teacher_id']})
        markup.add(types.InlineKeyboardButton(text=teacher['fullname'], callback_data=data))
    data = json.dumps({'teacher_id': 'cancel'})
    markup.add(types.InlineKeyboardButton(text='Отмена', callback_data=data))
    return markup


def keyboard_search_classrooms(classroom: str) -> InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    current_week = json.dumps({'current_week_classroom': classroom})
    next_week = json.dumps({'next_week_classroom': classroom})
    today = json.dumps({'today_classroom': classroom})
    tomorrow = json.dumps({'tomorrow_classroom': classroom})
    exams = json.dumps({'exams_classroom': classroom})
    markup.add(
        types.InlineKeyboardButton(text='На текущую неделю', callback_data=current_week),
        types.InlineKeyboardButton(text='На следующую неделю', callback_data=next_week)
    )
    markup.add(
        types.InlineKeyboardButton(text='На сегодня', callback_data=today),
        types.InlineKeyboardButton(text='На завтра', callback_data=tomorrow)
    )
    markup.add(types.InlineKeyboardButton(text='Экзамены', callback_data=exams))
    return markup
