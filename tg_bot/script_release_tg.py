"""Данный скрипт нужен для рассылки сообщения всем пользователям вк-бота"""

import os
import telebot
from telebot import types
from tools.storage import MongodbService

storage = MongodbService().get_instance()
TG_TOKEN = os.environ.get('TG_TOKEN')
bot = telebot.TeleBot(TG_TOKEN)


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
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    btn1 = types.KeyboardButton('Старт')
    markup.add(btn1)


    # Алгоритм рассылки сообщений
    for document in list_users:
        chat_id = document['chat_id']

        try:
            bot.send_message(chat_id=chat_id,
                             text=text,
                             reply_markup= markup)
            storage.delete_user_or_userdata(chat_id=chat_id)
        except Exception as e:
            pass
            storage.delete_user_or_userdata(chat_id=chat_id)

if input("Уверен? Напиши Да: ") == 'Да':
    print('Скрипт запущен')
    Script_message()
else:
    print('Отмена')
