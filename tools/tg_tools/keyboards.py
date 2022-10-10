from keyboa import Keyboa
from telebot.types import InlineKeyboardMarkup

user_role = [
    {'Я студент': '{"registration": "student"}'},
    {'Я преподователь': '{"registration": "teacher"}'}
]
start_menu = [
    {'Расписание 🗓': '{"start_menu": "schedule"}'},
    {'Ближайшая пара ⏱': '{"start_menu": "near_lesson"}'},
    {'Расписание на сегодня 🍏': '{"start_menu": "today_schedule"}'},
    {'Расписание на завтра 🍎': '{"start_menu": "tomorrow_schedule"}'},
    {'Поиск 🔎': '{"start_menu": "search"}'},
    {'Другое ⚡': '{"start_menu": "another"}'}
]


def keyboard_user_role() -> InlineKeyboardMarkup:
    return Keyboa(items=user_role)()


def keyboard_institutes(institutes: list) -> InlineKeyboardMarkup:
    return Keyboa(items=institutes)()


def keyboard_courses(courses: list) -> InlineKeyboardMarkup:
    return Keyboa(items=courses, copy_text_to_callback=True)()


def keyboard_groups(groups: list) -> InlineKeyboardMarkup:
    return Keyboa(items=groups)()


def keyboard_start_menu() -> InlineKeyboardMarkup:
    return Keyboa(items=start_menu)()
