from vkbottle.bot import Bot, Message
from vkbottle.keyboard import Keyboard, Text
import os

from app.storage import db

TOKEN = os.environ.get('VK')

bot = Bot(f"{os.environ.get('VK')}", debug="DEBUG")

def parametres_for_buttons_start_menu_vk(text, color):
    '''Возвращает параметры кнопок'''
    return {
        "action": {
            "type": "text",
            "payload": "{\"button\": \"" + "1" + "\"}",
            "label": f"{text}"
        },
        "color": f"{color}"
    }


def send_message_to_all_users(text: str, keyboard=None) -> ('status', 'message', 'exceptions'):
    exceptions = []
    users = db.users.find()
    count_users = db.users.count()

    for user in users:
        try:
            # отправляем сообщение
            # bot.send_message(text=text, reply_markup=keyboard)

        except Exception as e:
            print(e)
            exceptions.append(str(e))
    # если удалось отправить всем пользователям
    if not exceptions:
        return True, 'Сообщения отправлены', exceptions
    # если никому не удалось отправить
    elif len(exceptions) == count_users:
        return False, 'Сообщения не отправлены', exceptions
    # если удалось отправить не всем пользователям
    else:
        return True, 'Некоторые пользователи не получили сообщения', exceptions


def make_keyboard_start_menu():
    """Создаём основные кнопки"""
    keyboard = Keyboard(one_time=False)
    keyboard.add_row()
    keyboard.add_button(Text(label="Расписание"), color="primary")
    keyboard.add_button(Text(label="Ближайшая пара"), color="primary")
    keyboard.add_row()
    keyboard.add_button(Text(label="Расписание на сегодня"), color="default")
    keyboard.add_button(Text(label="Напоминание"), color="default")
    return keyboard