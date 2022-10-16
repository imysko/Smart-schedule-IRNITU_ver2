import pytz
from datetime import datetime, timedelta

from telebot import TeleBot

from db import getting_schedule
from db.mongo_storage import MongodbServiceTG
from tools.messages import error_messages, default_messages, schedule_messages
from tools.tg_tools import reply_keyboards
from tools.schedule_tools import schedule_conversion

TIMEZONE = pytz.timezone('Asia/Irkutsk')


def get_schedule(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.chat.id
    data = message.text
    user = storage.get_user(chat_id=chat_id)

    if 'Расписание 🗓' == data and user.get('group'):
        bot.send_message(
            chat_id=chat_id,
            text=default_messages['choose_period'],
            reply_markup=reply_keyboards.keyboard_choose_schedule()
        )

    elif 'Ближайшая пара ⏱' in data and user.get('group'):
        bot.send_message(
            chat_id=chat_id,
            text=default_messages['near_lesson'],
            reply_markup=reply_keyboards.keyboard_near_lesson()
        )

    if 'На текущую неделю' == data and user.get('group'):
        get_current_week(bot, message, storage)

    if 'На следующую неделю' == data and user.get('group'):
        get_next_week(bot, message, storage)

    elif 'Расписание на сегодня 🍏' == data and user.get('group'):
        get_today(bot, message, storage)

    elif 'Расписание на завтра 🍎' == data and user.get('group'):
        get_tomorrow(bot, message, storage)

    elif 'Экзамены' in data and user.get('group'):
        pass

    elif 'Текущая' in data and user.get('group'):
        pass

    elif 'Следующая' in data and user.get('group'):
        pass


def get_current_week(bot: TeleBot, message, storage: MongodbServiceTG):
    user_group = storage.get_user(message.chat.id)['group']

    # забахать проерку на пользователя: группа или препод

    schedule_list = getting_schedule.get_group_schedule(
        group_id=user_group,
        next_week=False
    )
    schedule_list = schedule_conversion.convert_lessons_group(schedule_list)

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
            text=schedule_messages['empty_current_week_lessons'],
        )


def get_next_week(bot: TeleBot, message, storage: MongodbServiceTG):
    user_group = storage.get_user(message.chat.id)['group']

    # забахать проерку на пользователя: группа или препод

    schedule_list = getting_schedule.get_group_schedule(
        group_id=user_group,
        next_week=True
    )
    schedule_list = schedule_conversion.convert_lessons_group(schedule_list)

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
            text=schedule_messages['empty_next_week_lessons'],
        )


def get_today(bot: TeleBot, message, storage: MongodbServiceTG):
    user_group = storage.get_user(message.chat.id)['group']

    # забахать проерку на пользователя: группа или препод

    schedule_list = getting_schedule.get_group_schedule(
        group_id=user_group,
        selected_date=datetime.now(TIMEZONE)
    )
    schedule_list = schedule_conversion.convert_lessons_group(schedule_list)

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
    #chat_id = message.chat.id

    #if storage.get_user(chat_id)['course'] != 'None':
    #    group = storage.get_user(chat_id=chat_id)['group']
    #    schedule = postgre_storage.get_schedule_by_group(group)

    #elif storage.get_user(chat_id)['course'] == 'None':
    #    group = storage.get_user(chat_id=chat_id)['group']
    #    schedule = None
    #    # get teacher schedule

    #if not schedule:
    #    bot.send_message(
    #        chat_id=chat_id,
    #        text=error_messages['currently_unavailable'],
    #        reply_markup=reply_keyboards.keyboard_start_menu()
    #    )
    #    return

    #week = 'even' if is_week_even is 1 else 'odd'

    user_group = storage.get_user(message.chat.id)['group']

    # забахать проерку на пользователя: группа или препод

    schedule_list = getting_schedule.get_group_schedule(
        group_id=user_group,
        selected_date=datetime.now(TIMEZONE) + timedelta(days=1)
    )
    schedule_list = schedule_conversion.convert_lessons_group(schedule_list)

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
