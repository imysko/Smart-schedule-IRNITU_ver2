from keyboa import Keyboa
from telebot.types import InlineKeyboardMarkup

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
