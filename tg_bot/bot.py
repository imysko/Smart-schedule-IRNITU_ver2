import asyncio
import json
import os
import time

from dotenv import load_dotenv
from telebot import TeleBot

from db.mongo_storage import MongodbServiceTG
from notifications import start_messages
from tg_bot.actions import commands
from tg_bot.actions.api import api
from tg_bot.actions.main_menu import main_menu, schedule, reminders
from tg_bot.actions.registration import group as student_registration
from tg_bot.actions.registration import teacher as teacher_registration
from tg_bot.actions.search import classrooms as classrooms_search
from tg_bot.actions.search import teachers as teachers_search
from tg_bot.actions.search import groups as groups_search
from tools.logger import logger
from tools.messages import error_messages, default_messages
from tools.tg_tools import reply_keyboards
from tools.content import *

load_dotenv()

TOKEN = os.environ.get('TG_TOKEN')

bot = TeleBot(token=TOKEN)
# start_messages.start_tg(bot)
storage = MongodbServiceTG().get_instance()


# ==================== Commands ==================== #
# /start
@bot.message_handler(
    func=lambda message: message.text in ['Начать', 'начать', 'Старт', 'старт', '/start', 'start'],
    content_types=['text'])
def start_handler(message):
    commands.start(
        bot=bot,
        message=message,
        storage=storage
    )


# /reg
@bot.message_handler(func=lambda message: message.text in ['Регистрация', 'регистрация', '/reg', 'reg'],
                     content_types=['text'])
def registration_handler(message):
    commands.registration(
        bot=bot,
        message=message,
        storage=storage
    )


# /help
@bot.message_handler(func=lambda message: message.text in ['Помощь', 'помощь', '/help', 'help'],
                     content_types=['text'])
def help_handler(message):
    commands.help(
        bot=bot,
        message=message,
        storage=storage
    )


# /about
@bot.message_handler(func=lambda message: message.text in ['О проекте', 'о проекте', '/about', 'about'],
                     content_types=['text'])
def about_handler(message):
    commands.about(
        bot=bot,
        message=message,
        storage=storage
    )


# /map
@bot.message_handler(func=lambda message: message.text in ['Карта', 'карта', '/map', 'map'],
                     content_types=['text'])
def map_handler(message):
    commands.show_map(
        bot=bot,
        message=message,
        storage=storage
    )


# /authors
@bot.message_handler(func=lambda message: message.text in ['Авторы', 'авторы', '/authors', 'authors'],
                     content_types=['text'])
def authors_handler(message):
    commands.authors(
        bot=bot,
        message=message,
        storage=storage,
    )


# ==================== Inline buttons handlers ==================== #
# Registration
@bot.callback_query_handler(func=lambda message: 'registration' in message.data)
def registration_handler(message):
    data = message.data
    callback = json.loads(data)['registration']

    if callback == 'student':
        storage.create_user(message.message.chat.id)
        student_registration.start_student_registration(
            bot=bot,
            message=message,
            storage=storage
        )

    elif callback == 'teacher':
        storage.create_user(message.message.chat.id)
        teacher_registration.start_teacher_registration(
            bot=bot,
            message=message,
            storage=storage
        )

    elif callback == 'back':
        storage.delete_user_or_userdata(message.message.chat.id)
        commands.registration(
            bot=bot,
            message=message.message,
            storage=storage,
            edit=True
        )

    logger.info(f'Inline button data: {data}')


@bot.callback_query_handler(func=lambda message: 'institute' in message.data)
def institute_registration_handler(message):
    data = message.data
    callback = json.loads(data)['institute']

    if callback == 'back':
        storage.create_user(message.message.chat.id)
        student_registration.start_student_registration(
            bot=bot,
            message=message,
            storage=storage
        )
    else:
        storage.save_or_update_user(
            chat_id=message.message.chat.id,
            institute=json.loads(data)['institute']
        )
        student_registration.select_course_student_registration(
            bot=bot,
            message=message,
            storage=storage
        )

    logger.info(f'Inline button data: {data}')


@bot.callback_query_handler(func=lambda message: 'course' in message.data)
def course_registration_handler(message):
    data = message.data
    callback = json.loads(data)['course']

    if callback == 'back':
        student_registration.select_course_student_registration(
            bot=bot,
            message=message,
            storage=storage
        )
    else:
        storage.save_or_update_user(
            chat_id=message.message.chat.id,
            course=json.loads(data)['course']
        )
        student_registration.select_group_student_registration(
            bot=bot,
            message=message,
            storage=storage
        )
    logger.info(f'Inline button data: {data}')


@bot.callback_query_handler(func=lambda message: 'register_group_id' in message.data)
def group_registration_handler(message):
    data = message.data
    group_id = json.loads(data)['register_group_id']

    storage.save_or_update_user(
        chat_id=message.message.chat.id,
        groups_ids=[group_id],
        teachers_ids=[]
    )

    student_registration.finish_student_registration(
        bot=bot,
        message=message,
        storage=storage
    )

    logger.info(f'Inline button data: {data}')


@bot.callback_query_handler(func=lambda message: 'register_teacher_id' in message.data)
def teacher_registration_finish_handler(message):
    teacher_registration.finish_teacher_registration_by_button(
        bot=bot,
        message=message,
        storage=storage
    )

    bot.delete_message(message.message.chat.id, message.message.id)
    logger.info(f'Inline button data: {message.data}')


# Search
@bot.message_handler(func=lambda message: message.text == 'Поиск 🔎', content_types=['text'])
def search_handler(message):
    chat_id = message.chat.id
    user = storage.get_user(chat_id)

    if user:
        bot.send_message(
            chat_id=chat_id,
            text=default_messages['choose_search_type'],
            reply_markup=reply_keyboards.keyboard_search_goal()
        )
        logger.info(f'Inline button data: {chat_id}')


@bot.message_handler(func=lambda message: message.text in content_search_type_buttons, content_types=['text'])
def search_type_handler(message):
    chat_id = message.chat.id
    if message.text == "Группы":
        groups_search.start_search_group(
            bot=bot,
            message=message,
            storage=storage,
        )
    elif message.text == "Преподаватели":
        teachers_search.start_search_teacher(
            bot=bot,
            message=message,
            storage=storage
        )
    elif message.text == 'Аудитории':
        classrooms_search.start_search_classroom(
            bot=bot,
            message=message,
            storage=storage,
        )
    logger.info(f'Inline button data: {chat_id}')


@bot.callback_query_handler(func=lambda message: any(word in message.data for word in content_search_classrooms))
def teacher_registration_finish_handler(message):
    classrooms_search.choose_period(
        message=message,
        bot=bot,
        storage=storage
    )
    logger.info(f'Inline button data: {message.data}')


@bot.callback_query_handler(func=lambda message: any(word in message.data for word in content_search_teachers))
def teacher_registration_finish_handler(message):
    teachers_search.choose_period(
        message=message,
        bot=bot,
        storage=storage
    )
    logger.info(f'Inline button data: {message.data}')


@bot.callback_query_handler(func=lambda message: any(word in message.data for word in content_search_groups))
def teacher_registration_finish_handler(message):
    groups_search.choose_period(
        message=message,
        bot=bot,
        storage=storage
    )
    logger.info(f'Inline button data: {message.data}')


@bot.callback_query_handler(func=lambda message: 'search_teacher_id' in message.data)
def teacher_registration_finish_handler(message):
    teachers_search.search_teacher_by_button(
        bot=bot,
        message=message,
        storage=storage
    )

    bot.delete_message(message.message.chat.id, message.message.id)
    logger.info(f'Inline button data: {message.data}')


# Reminder settings
@bot.callback_query_handler(func=lambda message: any(word in message.data for word in content_reminder_settings))
def reminder_settings_handler(message):
    reminders.reminder_settings(
        bot=bot,
        message=message,
        storage=storage
    )


# Schedule
@bot.message_handler(func=lambda message: message.text in content_schedule, content_types=['text'])
def schedule_handler(message):
    schedule.get_schedule(
        bot=bot,
        message=message,
        storage=storage
    )


# Reminders
@bot.message_handler(func=lambda message: message.text == 'Напоминание 📣', content_types=['text'])
def reminders_info_handler(message):
    reminders.reminder_info(
        bot=bot,
        message=message,
        storage=storage
    )


# Main buttons
@bot.message_handler(func=lambda message: message.text in content_main_menu_buttons, content_types=['text'])
def main_menu_buttons_handler(message):
    main_menu.processing_main_buttons(
        bot=bot,
        message=message,
        storage=storage
    )


# API
@bot.message_handler(func=lambda message: message.text in content_api, content_types=['text'])
def api_handler(message):
    asyncio.run(api.processing_api(
        bot=bot,
        message=message
    ))


@bot.message_handler(func=lambda message: '/api/schedule/month' in message.text, content_types=['text'])
def api_handler(message):
    asyncio.run(api.processing_api_schedule_month(
        bot=bot,
        message=message
    ))


@bot.message_handler(func=lambda message: '/api/schedule/two_weeks' in message.text, content_types=['text'])
def api_handler(message):
    asyncio.run(api.processing_api_schedule_two_weeks(
        bot=bot,
        message=message
    ))


# ==================== Text handler ==================== #
@bot.message_handler(content_types=['text'])
def text(message):
    chat_id = message.chat.id
    data = message.text
    user = storage.get_user(chat_id=chat_id)
    logger.info(f'Message data: {data}')

    if user:
        bot.send_message(
            chat_id=chat_id,
            text=error_messages['wrong_command'],
            reply_markup=reply_keyboards.keyboard_start_menu()
        )
    else:
        bot.send_message(
            chat_id=chat_id,
            text=error_messages['registration_not_finished']
        )


if __name__ == '__main__':
    bot.remove_webhook()
    logger.info('Bot started!')
    bot.infinity_polling(none_stop=True)
