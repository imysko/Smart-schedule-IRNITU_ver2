from keyboa import Keyboa
from pymongo import MongoClient
from pytz import timezone
from telebot import TeleBot

from tools.messages import registration_messages


def start(bot: TeleBot, message, storage, time_zone: timezone):
    chat_id = message.chat.id

    bot.send_message(
        chat_id=chat_id,
        text=registration_messages['new_registration'],
        reply_markup=Keyboa(items=[{'prep': 1}, {'user': 2}])()
    )
