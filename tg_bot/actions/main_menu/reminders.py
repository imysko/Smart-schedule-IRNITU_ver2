import json

from telebot import TeleBot

from db.mongo_storage import MongodbServiceTG
from tools.messages import reminder_messages
from tools.tg_tools import inline_keyboards


def get_reminders_status(time: int) -> str:
    if not time or time == 0:
        notifications_status = reminder_messages['status_disabled']
    else:
        notifications_status = reminder_messages['status_enabled'].format(time=time)
    return notifications_status


def reminder_info(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.chat.id
    user = storage.get_user(chat_id=chat_id)

    if user:
        time = user['notifications']
        if not time:
            time = 0
        bot.send_message(
            chat_id=chat_id,
            text=get_reminders_status(time),
            reply_markup=inline_keyboards.keyboard_set_notifications(time)
        )


def reminder_settings(bot: TeleBot, message, storage: MongodbServiceTG):
    pass
