from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api import VkUpload
import vk_api
import time
import json
import vk

#Токен для работы с ботом
#Ссылка на группу:https://vk.com/public198983266
token = "2b76b0ef7cf333a528691cf301f5a4f3b5183906b9b090e41be9b252303fb5c779176c4027b24df837007"
authorize = vk_api.VkApi(token=token)
longpoll= VkLongPoll(authorize)


def get_but(text, color):
    '''Возвращает параметры кнопок'''
    return {
        "action": {
        "type": "text",
        "payload": "{\"button\": \"" + "1" + "\"}",
        "label": f"{text}"
        },
        "color": f"{color}"
        }

#Клавиатура бота
keyboard = {
    "one_time": False,
    "buttons": [
        [get_but('Расписание', 'default'), get_but('Ближайшая пара', 'default')],
        [get_but('Напоминание', 'primary')]
]}


keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
keyboard = str(keyboard.decode('utf-8'))


def sender(id, text):
    '''Задаёт sender для отправки сообщения'''
    authorize.method('messages.send', {'user_id': id, 'message': text, 'random_id': 0, 'keyboard': keyboard})


def main():
    '''Ожидает сообщения от пользователя и даёт ответную реакцию'''
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                id = event.user_id
                msg = event.text.lower()
                sender(id, msg.upper())


if __name__ == "__main__":
    main()

