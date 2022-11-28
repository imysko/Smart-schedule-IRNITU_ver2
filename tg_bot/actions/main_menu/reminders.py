import json

from telebot import TeleBot
from telebot.apihelper import ApiTelegramException

from db.getting_schedule import get_teacher_schedule, get_group_schedule
from db.mongo_storage import MongodbServiceTG
from tools.logger import logger
from tools.schedule_tools.notifications import get_reminders_status, calculating_reminder_times
from tools.tg_tools import inline_keyboards


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
    data = message.data

    if 'decrease_reminder_time' in data:
        decrease_time(bot, message)

    elif 'increase_reminder_time' in data:
        increase_time(bot, message)

    elif 'save_reminder_time' in data:
        save_time(bot, message, storage)


def decrease_time(bot: TeleBot, message):
    chat_id = message.message.chat.id
    message_id = message.message.message_id
    data = message.data

    data = json.loads(data)
    time = data['decrease_reminder_time']
    if time == 0:
        return
    time -= 5

    if time < 0:
        time = 0

    try:
        bot.edit_message_reply_markup(
            message_id=message_id,
            chat_id=chat_id,
            reply_markup=inline_keyboards.keyboard_set_notifications(time)
        )
    except ApiTelegramException as ex:
        logger.error(ex)


def increase_time(bot: TeleBot, message):
    chat_id = message.message.chat.id
    message_id = message.message.message_id
    data = message.data

    data = json.loads(data)
    time = data['increase_reminder_time']
    time += 5

    try:
        bot.edit_message_reply_markup(
            message_id=message_id,
            chat_id=chat_id,
            reply_markup=inline_keyboards.keyboard_set_notifications(time)
        )
    except ApiTelegramException as ex:
        logger.error(ex)


def save_time(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.message.chat.id
    message_id = message.message.message_id
    data = message.data

    data = json.loads(data)
    time = data['save_reminder_time']

    group = storage.get_user(chat_id)['group_id']

    if storage.get_user(chat_id)['course'] == 'None':
        schedule = get_teacher_schedule(group)
    else:
        schedule = get_group_schedule(group)

    if time > 0:
        reminders = calculating_reminder_times(schedule=schedule, time=int(time))
    else:
        reminders = []

    storage.save_or_update_user(
        chat_id=chat_id,
        notifications=time,
        reminders=reminders
    )

    try:
        bot.edit_message_text(
            message_id=message_id,
            chat_id=chat_id,
            text=get_reminders_status(time),
            reply_markup=inline_keyboards.keyboard_set_notifications(time)
        )
    except ApiTelegramException as ex:
        logger.error(ex)
