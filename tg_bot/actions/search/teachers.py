import json
import re
from datetime import datetime, timedelta

import pytz
from telebot import TeleBot

from db import postgre_storage, getting_schedule
from db.mongo_storage import MongodbServiceTG
from tg_bot.actions.registration.teacher import find_teacher
from tools.messages import search_messages, default_messages, schedule_messages
from tools.schedule_tools import schedule_conversion
from tools.schedule_tools.utils import get_now
from tools.tg_tools import reply_keyboards, inline_keyboards


def start_search_teacher(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.chat.id
    user = storage.get_user(chat_id)

    if user:
        msg = bot.send_message(
            chat_id=chat_id,
            text=search_messages['input_teacher'],
            reply_markup=reply_keyboards.keyboard_main_menu()
        )
        bot.register_next_step_handler(msg, search_teacher, bot=bot, storage=storage)


def search_teacher(message, bot: TeleBot, storage):
    chat_id = message.chat.id
    message_id = message.message_id
    text = message.text

    if message.content_type != 'text':
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

    teachers_list = postgre_storage.get_teachers()
    teachers = list(filter(lambda user: user['fullname'] == text, teachers_list))

    if teachers:
        bot.send_message(
            chat_id=chat_id,
            text=search_messages['select_type_search'],
            reply_markup=inline_keyboards.keyboard_search(teachers[0]['teacher_id'], 'teacher')
        )
    else:
        teachers = find_teacher(text, teachers_list)
        if teachers:
            msg = bot.send_message(
                chat_id=chat_id,
                text=search_messages['check_input'],
                reply_markup=reply_keyboards.keyboard_main_menu()
            )
            bot.register_next_step_handler(msg, search_teacher, bot=bot, storage=storage, last_msg=msg)
        else:
            bot.send_message(
                chat_id=chat_id,
                text=search_messages['probably_you_mean'],
                reply_markup=inline_keyboards.keyboard_search_with_possible_teachers(teachers)
            )


def search_teacher_by_button(message, bot: TeleBot, storage: MongodbServiceTG):
    chat_id = message.message.chat.id
    data = json.loads(message.data)

    teacher_id = data['search_teacher_id']
    teachers_list = postgre_storage.get_teachers()

    teacher = list(filter(lambda x: x['teacher_id'] == teacher_id, teachers_list))[0]['teacher_id']
    bot.send_message(
        chat_id=chat_id,
        text=search_messages['select_type_search'],
        reply_markup=inline_keyboards.keyboard_search(teacher, 'teacher')
    )


def choose_period(message, bot: TeleBot, storage: MongodbServiceTG):
    data = message.data

    if 'current_week_teacher' in data:
        get_current_week(bot, message, storage)
    elif 'next_week_teacher' in data:
        get_next_week(bot, message, storage)
    elif 'today_teacher' in data:
        get_today(bot, message, storage)
    elif 'tomorrow_teacher' in data:
        get_tomorrow(bot, message, storage)


def get_current_week(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.message.chat.id

    teacher_id = json.loads(message.data)['current_week_teacher']

    schedule_list = getting_schedule.get_teacher_schedule(
        teacher_id=teacher_id,
        next_week=False
    )
    schedule_list = schedule_conversion.convert_lessons_teachers(schedule_list)

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

    teacher_id = json.loads(message.data)['next_week_teacher']

    schedule_list = getting_schedule.get_teacher_schedule(
        teacher_id=teacher_id,
        next_week=True
    )
    schedule_list = schedule_conversion.convert_lessons_teachers(schedule_list)

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

    teacher_id = json.loads(message.data)['today_teacher']

    schedule_list = getting_schedule.get_teacher_schedule(
        teacher_id=teacher_id,
        selected_date=get_now()
    )
    schedule_list = schedule_conversion.convert_lessons_teachers(schedule_list)

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

    teacher_id = json.loads(message.data)['tomorrow_teacher']

    schedule_list = getting_schedule.get_teacher_schedule(
        teacher_id=teacher_id,
        selected_date=get_now() + timedelta(days=1)
    )
    schedule_list = schedule_conversion.convert_lessons_teachers(schedule_list)

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
