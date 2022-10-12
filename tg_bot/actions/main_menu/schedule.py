from telebot import TeleBot

from db import postgre_storage, data_conversion
from db.mongo_storage import MongodbServiceTG
from db.postgre_storage import is_week_even
from tools.messages import error_messages, default_messages
from tools.tg_tools import reply_keyboards
from tools.schedule_tools import schedule_conversion


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
    schedule_list = data_conversion.convert_schedule(
        pg_schedule=postgre_storage.get_schedule_by_group(user_group),
        next_week=False
    )

    for day in schedule_conversion.convert_lessons(schedule_list):
        bot.send_message(
            chat_id=message.chat.id,
            text=day
        )


def get_next_week(bot: TeleBot, message, storage: MongodbServiceTG):
    user_group = storage.get_user(message.chat.id)['group']
    schedule_list = data_conversion.convert_schedule(
        pg_schedule=postgre_storage.get_schedule_by_group(user_group),
        next_week=True
    )

    for day in schedule_conversion.convert_lessons(schedule_list):
        bot.send_message(
            chat_id=message.chat.id,
            text=day
        )


def get_today(bot: TeleBot, message, storage: MongodbServiceTG):
    pass


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
    pass
