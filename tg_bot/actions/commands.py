from pymongo import MongoClient
from pytz import timezone
from telebot import TeleBot

from tools.messages import registration_messages, other_messages
from tools.tg_tools import keyboards


def start(bot: TeleBot, message, storage, time_zone: timezone):
    chat_id = message.chat.id

    bot.send_message(
        chat_id=chat_id,
        text=registration_messages['new_registration'],
        reply_markup=keyboards.keyboard_user_role()
    )


def registration(bot: TeleBot, message, storage, time_zone: timezone):
    chat_id = message.chat.id

    bot.send_message(
        chat_id=chat_id,
        text=registration_messages['repeat_registration'],
        reply_markup=keyboards.keyboard_user_role()
    )


def help(bot: TeleBot, message, storage, time_zone: timezone):
    chat_id = message.chat.id
    bot.send_message(
        chat_id=chat_id,
        text=other_messages['help_message']
    )


def about(bot: TeleBot, message, storage, time_zone: timezone):
    chat_id = message.chat.id

    bot.send_message(
        chat_id=chat_id,
        parse_mode='HTML',
        text=other_messages['about_message']
    )


def show_map(bot: TeleBot, message, storage, time_zone: timezone):
    chat_id = message.chat.id
    bot.send_message(
        chat_id,
        text=other_messages['map_message']
    )


def authors(bot: TeleBot, message, storage, time_zone: timezone):
    chat_id = message.chat.id

    bot.send_message(
        chat_id=chat_id,
        parse_mode='HTML',
        text=other_messages['author_message']
    )
