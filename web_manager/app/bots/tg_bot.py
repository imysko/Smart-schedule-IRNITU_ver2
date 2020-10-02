import telebot
from telebot import types
import os

from app.storage import db

TOKEN = os.environ.get('TG_TOKEN')

bot = telebot.TeleBot(TOKEN, threaded=False)


def send_message_to_all_users(text: str, keyboard=None) -> ('status', 'message', 'exceptions'):
    exceptions = []
    users = db.users.find()
    count_users = db.users.count()

    for user in users:
        try:
            # отправляем сообщение
            bot.send_message(chat_id=user['chat_id'], text=text, reply_markup=keyboard)
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
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    btn1 = types.KeyboardButton('Расписание')
    btn2 = types.KeyboardButton('Ближайшая пара')
    btn3 = types.KeyboardButton('Расписание на сегодня')
    btn4 = types.KeyboardButton('Напоминания')
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    return markup
