import telebot
import os

from app.storage import db

TOKEN = os.environ.get('TG_TOKEN')

bot = telebot.TeleBot(TOKEN, threaded=False)


def send_message_to_all_users(text: str) -> ('status', 'message', 'exceptions'):
    exceptions = []
    users = db.users.find()
    count_users = db.users.count()

    for user in users:
        try:
            # отправляем сообщение
            bot.send_message(chat_id=user['chat_id'], text=text)
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
