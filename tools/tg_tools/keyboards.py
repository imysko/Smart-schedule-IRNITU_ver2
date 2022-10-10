from keyboa import Keyboa
from telebot.types import InlineKeyboardMarkup

user_role = [
    {'Я студент': 1},
    {'Я преподователь': 2}
]


def keyboard_user_role() -> InlineKeyboardMarkup:
    return Keyboa(items=user_role)()


def keyboard_institutes(institutes: list) -> InlineKeyboardMarkup:
    return Keyboa(items=institutes)()


def keyboard_courses(courses: list) -> InlineKeyboardMarkup:
    return Keyboa(items=courses, copy_text_to_callback=True)()


def keyboard_groups(groups: list) -> InlineKeyboardMarkup:
    return Keyboa(items=groups)()
