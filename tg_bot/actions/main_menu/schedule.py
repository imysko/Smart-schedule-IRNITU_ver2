import pytz
from datetime import datetime, timedelta

from telebot import TeleBot

from db import getting_schedule
from db.mongo_storage import MongodbServiceTG
from tools.messages import error_messages, default_messages, schedule_messages
from tools.schedule_tools.utils import get_now
from tools.tg_tools import reply_keyboards
from tools.schedule_tools import schedule_conversion


def get_schedule(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.chat.id
    data = message.text
    user = storage.get_user(chat_id=chat_id)

    if user.get('groups_ids') or user.get('teachers_ids'):
        if 'Расписание 🗓' == data:
            bot.send_message(
                chat_id=chat_id,
                text=default_messages['choose_period'],
                reply_markup=reply_keyboards.keyboard_choose_schedule()
            )

        elif 'Ближайшая пара ⏱' in data:
            bot.send_message(
                chat_id=chat_id,
                text=default_messages['near_lesson'],
                reply_markup=reply_keyboards.keyboard_near_lesson()
            )

        if 'На текущую неделю' == data:
            get_week_schedule(bot, message, storage, next_week=False)

        if 'На следующую неделю' == data:
            get_week_schedule(bot, message, storage, next_week=True)

        elif 'Расписание на сегодня 🍏' == data:
            get_today(bot, message, storage)

        elif 'Расписание на завтра 🍎' == data:
            get_tomorrow(bot, message, storage)

        elif 'Текущая' in data:
            get_current_lesson(bot, message, storage)

        elif 'Следующая' in data:
            get_near_lesson(bot, message, storage)


def get_week_schedule(bot: TeleBot, message, storage: MongodbServiceTG, next_week):
    chat_id = message.chat.id

    user = storage.get_user(chat_id)
    teachers_ids = user['teachers_ids']
    groups_ids = user['groups_ids']
    empty_message = schedule_messages['empty_next_week_lessons'] if next_week else schedule_messages['empty_current_week_lessons']

    if groups_ids:
        schedule_list = getting_schedule.get_group_schedule(
            group_id=groups_ids[0],
            next_week=next_week
        )
        schedule_list = schedule_conversion.convert_lessons_group(schedule_list)
        if schedule_list:
            for day in schedule_list:
                bot.send_message(
                    chat_id=message.chat.id,
                    text=day,
                    parse_mode='HTML'
                )
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text=empty_message,
            )

    if teachers_ids:
        schedule_list = getting_schedule.get_teacher_schedule(
            teacher_id=teachers_ids[0],
            next_week=next_week
        )
        schedule_list = schedule_conversion.convert_lessons_teachers(schedule_list)
        if schedule_list:
            for day in schedule_list:
                bot.send_message(
                    chat_id=message.chat.id,
                    text=day,
                    parse_mode='HTML'
                )
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text=empty_message,
            )


def get_today(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.chat.id

    user_group = storage.get_user(chat_id)['group_id']

    if storage.get_user(chat_id)['institute'] != 'teacher':
        schedule_list = getting_schedule.get_group_schedule(
            group_id=user_group,
            selected_date=get_now()
        )
        schedule_list = schedule_conversion.convert_lessons_group(schedule_list)
    else:
        schedule_list = getting_schedule.get_teacher_schedule(
            teacher_id=user_group,
            selected_date=get_now()
        )
        schedule_list = schedule_conversion.convert_lessons_teachers(schedule_list)

    if len(schedule_list):
        for day in schedule_list:
            bot.send_message(
                chat_id=message.chat.id,
                text=day,
                parse_mode='HTML'
            )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text=schedule_messages['empty_today_lessons'],
        )


def get_tomorrow(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.chat.id

    user_group = storage.get_user(chat_id)['group_id']

    if storage.get_user(chat_id)['institute'] != 'teacher':
        schedule_list = getting_schedule.get_group_schedule(
            group_id=user_group,
            selected_date=get_now() + timedelta(days=1)
        )
        schedule_list = schedule_conversion.convert_lessons_group(schedule_list)
    else:
        schedule_list = getting_schedule.get_teacher_schedule(
            teacher_id=user_group,
            selected_date=get_now() + timedelta(days=1)
        )
        schedule_list = schedule_conversion.convert_lessons_teachers(schedule_list)

    if len(schedule_list):
        for day in schedule_list:
            bot.send_message(
                chat_id=message.chat.id,
                text=day,
                parse_mode='HTML'
            )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text=schedule_messages['empty_tomorrow_lessons'],
        )


def get_current_lesson(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.chat.id

    user_group = storage.get_user(chat_id)['group_id']

    if storage.get_user(chat_id)['institute'] != 'teacher':
        lessons = getting_schedule.get_group_current_lesson(group_id=user_group)
        lessons = schedule_conversion.convert_current_lessons_group(lessons)
    else:
        lessons = getting_schedule.get_teacher_current_lesson(teacher_id=user_group)
        lessons = schedule_conversion.convert_current_lessons_teacher(lessons)

    if len(lessons):
        bot.send_message(
            chat_id=message.chat.id,
            text=lessons,
            parse_mode='HTML'
        )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text=schedule_messages['empty_current_lessons'],
        )


def get_near_lesson(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.chat.id

    user = storage.get_user(chat_id)

    if user['groups_ids']:
        lessons = getting_schedule.get_group_near_lesson(group_id=user['groups_ids'][0])
        lessons = schedule_conversion.convert_near_lessons_group(lessons)
        if lessons:
            bot.send_message(
                chat_id=message.chat.id,
                text=lessons,
                parse_mode='HTML'
            )
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text=schedule_messages['empty_near_lessons'],
            )
    if user['teachers_ids']:
        lessons = getting_schedule.get_teacher_near_lesson(teacher_id=user['teachers_ids'][0])
        lessons = schedule_conversion.convert_near_lessons_teacher(lessons)
        if lessons:
            bot.send_message(
                chat_id=message.chat.id,
                text=lessons,
                parse_mode='HTML'
            )
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text=schedule_messages['empty_near_lessons'],
            )

