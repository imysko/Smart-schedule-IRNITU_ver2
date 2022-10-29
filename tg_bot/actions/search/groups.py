import json
import re
from datetime import datetime, timedelta

import pytz
from telebot import TeleBot

from db import postgre_storage, getting_schedule
from db.mongo_storage import MongodbServiceTG
from tools.messages import search_messages, default_messages, schedule_messages
from tools.schedule_tools import schedule_conversion
from tools.tg_tools import reply_keyboards, inline_keyboards

TIMEZONE = pytz.timezone('Asia/Irkutsk')

def start_search_group(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.chat.id
    user = storage.get_user(chat_id)

    if user:
        msg = bot.send_message(
            chat_id=chat_id,
            text=search_messages['input_group'],
            reply_markup=reply_keyboards.keyboard_main_menu()
        )
        bot.register_next_step_handler(msg, search_group, bot=bot, storage=storage)


def search_group(message, bot: TeleBot, storage):
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

    groups = postgre_storage.get_groups()
    groups_names = list(map(lambda x: x['name'].lower(), groups))
    matches = list(filter(re.compile(f'{text.lower()}').match, groups_names))

    if len(matches) == 1:
        group_id = list(filter(lambda x: x['name'].lower() == matches[0], groups))[0]['group_id']
        bot.send_message(
            chat_id=chat_id,
            text=search_messages['select_type_search'],
            reply_markup=inline_keyboards.keyboard_search(group_id, 'group')
        )
    else:
        msg = bot.send_message(
            chat_id=chat_id,
            text=search_messages['check_input'],
            reply_markup=reply_keyboards.keyboard_main_menu()
        )
        bot.register_next_step_handler(msg, search_group, bot=bot, storage=storage)


def choose_period(message, bot: TeleBot, storage: MongodbServiceTG):
    data = message.data

    if 'current_week_group' in data:
        get_current_week(bot, message, storage)
    elif 'next_week_group' in data:
        get_next_week(bot, message, storage)
    elif 'today_group' in data:
        get_today(bot, message, storage)
    elif 'tomorrow_group' in data:
        get_tomorrow(bot, message, storage)
    elif 'exams_group' in data:
        pass


def get_current_week(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.message.chat.id

    group_id = json.loads(message.data)['current_week_group']

    schedule_list = getting_schedule.get_group_schedule(
        group_id=group_id,
        next_week=False
    )
    schedule_list = schedule_conversion.convert_lessons_group(schedule_list)

    if len(schedule_list):
        for day in schedule_list:
            bot.send_message(
                chat_id=message.message.chat.id,
                text=day,
                parse_mode='HTML'
            )
    else:
        bot.send_message(
            chat_id=message.message.chat.id,
            text=schedule_messages['empty_current_week_lessons'],
        )


def get_next_week(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.message.chat.id

    group_id = json.loads(message.data)['next_week_group']

    schedule_list = getting_schedule.get_group_schedule(
        group_id=group_id,
        next_week=True
    )
    schedule_list = schedule_conversion.convert_lessons_group(schedule_list)

    if len(schedule_list):
        for day in schedule_list:
            bot.send_message(
                chat_id=message.message.chat.id,
                text=day,
                parse_mode='HTML'
            )
    else:
        bot.send_message(
            chat_id=message.message.chat.id,
            text=schedule_messages['empty_next_week_lessons'],
        )


def get_today(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.message.chat.id

    group_id = json.loads(message.data)['today_group']

    schedule_list = getting_schedule.get_group_schedule(
        group_id=group_id,
        selected_date=datetime.now(TIMEZONE),
    )
    schedule_list = schedule_conversion.convert_lessons_group(schedule_list)

    if len(schedule_list):
        for day in schedule_list:
            bot.send_message(
                chat_id=message.message.chat.id,
                text=day,
                parse_mode='HTML'
            )
    else:
        bot.send_message(
            chat_id=message.message.chat.id,
            text=schedule_messages['empty_today_lessons'],
        )


def get_tomorrow(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.message.chat.id

    group_id = json.loads(message.data)['tomorrow_group']

    schedule_list = getting_schedule.get_group_schedule(
        group_id=group_id,
        selected_date=datetime.now(TIMEZONE) + timedelta(days=1),
    )
    schedule_list = schedule_conversion.convert_lessons_group(schedule_list)

    if len(schedule_list):
        for day in schedule_list:
            bot.send_message(
                chat_id=message.message.chat.id,
                text=day,
                parse_mode='HTML'
            )
    else:
        bot.send_message(
            chat_id=message.message.chat.id,
            text=schedule_messages['empty_tomorrow_lessons'],
        )
