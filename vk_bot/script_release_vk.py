"""Данный скрипт нужен для рассылки сообщения всем пользователям вк-бота"""

import os
import vk_api
import json
from tools.storage import MongodbService

storage = MongodbService().get_instance()
VK_TOKEN = os.environ.get('VK')
bot = vk_api.VkApi(token=VK_TOKEN)


def Script_message():
    # Список всех пользователей
    list_users = storage.get_users_for_script()
    # Текст для сообщения
    text = '❗❗❗❗❗❗❗❗❗ \n' \
           'Внимание, внимание, внимание!\n' \
           'Пользователь, мы очень рады представить "Умное расписание 3.0" 🥳🥳🥳\n' \
           'Самые главные нововведения:\n' \
           '- расписание для преподавателей\n' \
           '- поиск расписания преподавателей и других групп\n' \
           '- изменения интерфейса и подсказок\n' \
           'Пройдите заново регистрацию, чтобы получить доступ к обновлённой версии бота! Желаем приятного использования!\n' \
           '❗❗❗❗❗❗❗❗❗\n' \
           '\n' \
           'Нажмите или напишите "Начать"😉'

    # Клавиатура с кнопкой
    keyboard = {
        "one_time": False,
        "buttons": [
            [{
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"1\"}",
                    "label": "Начать"
                },
                "color": "positive"
            }]
        ]
    }

    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))

    # Алгоритм рассылки сообщений
    for document in list_users:
        chat_id = document['chat_id']

        try:
            bot.method('messages.send', {'user_id': chat_id, 'message': text, 'random_id': 0, 'keyboard': keyboard})
            storage.delete_vk_user_or_userdata(chat_id=chat_id)
        except Exception as e:
            pass
            storage.delete_vk_user_or_userdata(chat_id=chat_id)


Script_message()
