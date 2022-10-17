import re

from telebot import TeleBot

from db import postgre_storage
from db.mongo_storage import MongodbServiceTG
from tools.messages import search_messages, default_messages
from tools.tg_tools import reply_keyboards, inline_keyboards


def start_search_classroom(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.chat.id
    user = storage.get_user(chat_id)

    if user:
        msg = bot.send_message(
            chat_id=chat_id,
            text=search_messages['input_classroom'],
            reply_markup=reply_keyboards.keyboard_main_menu()
        )
        bot.register_next_step_handler(msg, search_classroom, bot=bot, storage=storage)


def search_classroom(message, bot: TeleBot, storage):
    chat_id = message.chat.id
    message_id = message.message_id
    text = message.text

    if message.content_type != 'text' or len(text) < 2:
        text = ''

    if text == 'Основное меню':
        bot.delete_message(
            message_id=message_id,
            chat_id=chat_id
        )
        bot.send_message(
            chat_id=chat_id,
            text=default_messages['start_menu'],
            reply_markup=reply_keyboards.keyboard_start_menu()
        )
        return

    classrooms = postgre_storage.get_classrooms()
    classrooms_names = list(map(lambda x: x['name'].lower(), classrooms))
    matches = list(filter(re.compile(f'{text.lower()}').match, classrooms_names))

    if len(matches) == 1:
        classroom_id = list(filter(lambda x: x['name'].lower() == matches[0], classrooms))[0]['classroom_id']
        bot.send_message(
            chat_id=chat_id,
            text=search_messages['select_type_search'],
            reply_markup=inline_keyboards.keyboard_search_classroom(classroom_id)
        )
    else:
        msg = bot.send_message(
            chat_id=chat_id,
            text=search_messages['check_input'],
            reply_markup=reply_keyboards.keyboard_main_menu()
        )
        bot.register_next_step_handler(msg, search_classroom, bot=bot, storage=storage, last_msg=msg)


def choose_period(message, bot: TeleBot, storage: MongodbServiceTG):
    data = message.data

    if 'current_week_classroom' in data:
        get_current_week(bot, message, storage)
    elif 'next_week_classroom' in data:
        get_next_week(bot, message, storage)
    elif 'today_classroom' in data:
        get_today(bot, message, storage)
    elif 'tomorrow_classroom' in data:
        get_tomorrow(bot, message, storage)
    elif 'exams_classrooms' in data:
        pass


def get_current_week(bot: TeleBot, message, storage: MongodbServiceTG):
    pass


def get_next_week(bot: TeleBot, message, storage: MongodbServiceTG):
    pass


def get_today(bot: TeleBot, message, storage: MongodbServiceTG):
    pass


def get_tomorrow(bot: TeleBot, message, storage: MongodbServiceTG):
    pass
