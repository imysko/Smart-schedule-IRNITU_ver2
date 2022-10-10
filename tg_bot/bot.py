import os
import time

import pytz
from dotenv import load_dotenv
from telebot import TeleBot

from db.mongo_storage import MongodbService
from tg_bot.actions import commands
from tg_bot.actions.registration import student as student_registration
from tg_bot.actions.registration import teacher as teacher_registration
from tools.logger import logger
from tools.messages import error_messages

load_dotenv()

TOKEN = os.environ.get('TG_TOKEN')
TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk')

bot = TeleBot(token=TOKEN)

storage = MongodbService().get_instance()

content_schedule = ['Расписание 🗓', 'Ближайшая пара ⏱', 'Расписание на сегодня 🍏', 'На текущую неделю',
                    'На следующую неделю',
                    'Расписание на завтра 🍎', 'Следующая', 'Текущая', 'Экзамены']

content_main_menu_buttons = ['Основное меню', '<==Назад', 'Другое ⚡']

content_students_registration = ['institute', 'course', 'group']
content_reminder_settings = [
    'notification_btn', 'del_notifications', 'add_notifications', 'save_notifications']
content_prep_group = ["found_prep", "prep_list"]
content_aud = ["search_aud", "menu_aud"]


# Commands

# /start
@bot.message_handler(
    func=lambda message: message.text in ['Начать', 'начать', 'Старт', 'старт', '/start', 'start'],
    content_types=['text'])
def start_handler(message):
    commands.start(
        bot=bot,
        message=message,
        storage=storage,
        time_zone=TZ_IRKUTSK
    )


# /reg
@bot.message_handler(func=lambda message: message.text in ['Регистрация', 'регистрация', '/reg', 'reg'],
                     content_types=['text'])
def registration_handler(message):
    commands.registration(
        bot=bot,
        message=message,
        storage=storage,
        time_zone=TZ_IRKUTSK
    )


# /help
@bot.message_handler(func=lambda message: message.text in ['Помощь', 'помощь', '/help', 'help'],
                     content_types=['text'])
def help_handler(message):
    commands.help(
        bot=bot,
        message=message,
        storage=storage,
        time_zone=TZ_IRKUTSK
    )


# /about
@bot.message_handler(func=lambda message: message.text in ['О проекте', 'о проекте', '/about', 'about'],
                     content_types=['text'])
def about_handler(message):
    commands.about(
        bot=bot,
        message=message,
        storage=storage,
        time_zone=TZ_IRKUTSK
    )


# /map
@bot.message_handler(func=lambda message: message.text in ['Карта', 'карта', '/map', 'map'],
                     content_types=['text'])
def map_handler(message):
    commands.show_map(
        bot=bot,
        message=message,
        storage=storage,
        time_zone=TZ_IRKUTSK
    )


# /authors
@bot.message_handler(func=lambda message: message.text in ['Авторы', 'авторы', '/authors', 'authors'],
                     content_types=['text'])
def authors_handler(message):
    commands.authors(
        bot=bot,
        message=message,
        storage=storage,
        time_zone=TZ_IRKUTSK
    )


# Inline buttons handlers

# Registration
@bot.callback_query_handler(func=lambda message: 'registration' in message.data)
def registration_handler(message):
    data = message.data

    if data == '{"registration": "student"}':
        student_registration.start_student_registration(
            bot=bot,
            message=message,
            storage=storage
        )

        # пользователь - студент и сохранить id чата
    elif data == '{"registration": "teacher"}':
        teacher_registration.start_teacher_registration(
            bot=bot,
            message=message,
            storage=storage
        )

        # пользователь - преподаватель и сохранить id чата
    elif data == '{"registration": "back"}':
        commands.registration(
            bot=bot,
            message=message.message,
            storage=storage,
            time_zone=TZ_IRKUTSK,
            edit=True
        )

        # удалить информацию о пользователе

    logger.info(f'Inline button data: {data}')


@bot.callback_query_handler(func=lambda message: 'institute' in message.data)
def institute_registration_handler(message):
    data = message.data

    if data == '{"institute": "back"}':
        student_registration.start_student_registration(
            bot=bot,
            message=message,
            storage=storage
        )

        # удалить институт из монго
    else:
        student_registration.select_course_student_registration(
            bot=bot,
            message=message,
            storage=storage
        )

        # сохранить институт в монго

    logger.info(f'Inline button data: {data}')


@bot.callback_query_handler(func=lambda message: 'course' in message.data)
def course_registration_handler(message):
    data = message.data

    if data == '{"course": "back"}':
        student_registration.select_course_student_registration(
            bot=bot,
            message=message,
            storage=storage
        )

        # удалить курс из монго
    else:
        student_registration.select_group_student_registration(
            bot=bot,
            message=message,
            storage=storage
        )

        # сохранить курс в монго

    logger.info(f'Inline button data: {data}')


@bot.callback_query_handler(func=lambda message: 'group' in message.data)
def group_registration_handler(message):
    data = message.data

    # сохранить группу в монго

    logger.info(f'Inline button data: {data}')


# Search
@bot.message_handler(
    func=lambda message: message.text == 'Группы и преподаватели' or message.text == 'Аудитории',
    content_types=['text'])
def reminders_info_handler(message):
    data = message.chat.id
    if message.text == "Группы и преподаватели":
        # Clear keyboard
        # Start search
        pass
    elif message.text == 'Аудитории':
        # Clear keyboard
        # Start search
        pass
    logger.info(f'Inline button data: {data}')


# Reminder settings
@bot.callback_query_handler(func=lambda message: any(word in message.data for word in content_reminder_settings))
def reminder_settings_handler(message):
    data = message.data
    # Open settings
    logger.info(f'Inline button data: {data}')


# Schedule
@bot.message_handler(func=lambda message: message.text in content_schedule, content_types=['text'])
def schedule_handler(message):
    # Send schedule
    pass


# Reminders
@bot.message_handler(func=lambda message: message.text == 'Напоминание 📣', content_types=['text'])
def reminders_info_handler(message):
    # Send reminders info
    pass


# Main buttons
@bot.message_handler(func=lambda message: message.text in content_main_menu_buttons, content_types=['text'])
def main_menu_buttons_handler(message):
    # Send main buttons
    pass


# Text handler
@bot.message_handler(content_types=['text'])
def text(message):
    chat_id = message.chat.id
    data = message.text
    user = storage.get_tg_user(chat_id=chat_id)
    logger.info(f'Message data: {data}')

    if user:
        # Clear keyboard
        bot.send_message(chat_id, text=error_messages['wrong_command'])
    else:
        bot.send_message(chat_id, text=error_messages['registration_not_finished'])


if __name__ == '__main__':
    bot.remove_webhook()
    logger.info('Bot started!')
    while True:
        try:
            bot.infinity_polling(none_stop=True)
        except Exception as e:
            logger.error(e)
            time.sleep(3)
