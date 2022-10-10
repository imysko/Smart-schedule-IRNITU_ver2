import os
import time

import pytz
from dotenv import load_dotenv
from telebot import TeleBot

from db.mongo_storage import MongodbService
from tg_bot.actions import commands
from tools import statistics
from tools.logger import logger
from tools.messages import error_messages

load_dotenv()

TOKEN = os.environ.get('TG_TOKEN')
TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk')

bot = TeleBot(token=TOKEN)

storage = None
# storage = MongodbService().get_instance()

content_schedule = ['Расписание 🗓', 'Ближайшая пара ⏱', 'Расписание на сегодня 🍏', 'На текущую неделю',
                    'На следующую неделю',
                    'Расписание на завтра 🍎', 'Следующая', 'Текущая', 'Экзамены']
content_main_menu_buttons = ['Основное меню', '<==Назад', 'Другое ⚡']
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
    pass


# /help
@bot.message_handler(func=lambda message: message.text in ['Помощь', 'помощь', '/help', 'help'],
                     content_types=['text'])
def help_handler(message):
    pass


# /about
@bot.message_handler(func=lambda message: message.text in ['О проекте', 'о проекте', '/about', 'about'],
                     content_types=['text'])
def about_handler(message):
    pass


# /authors
@bot.message_handler(func=lambda message: message.text in ['Авторы', 'авторы', '/authors', 'authors'],
                     content_types=['text'])
def authors_handler(message):
    pass


# Inline buttons handlers

# Registration
@bot.callback_query_handler(func=lambda message: 'registration' in message.data)
def registration_handler(message):
    data = message.data
    if data == '{"registration": "student"}':
        # Start student registration
        pass
    elif data == '{"registration": "teacher"}':
        # Start teacher registration
        pass
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
@bot.callback_query_handler(
    func=lambda message: any(word in message.data for word in content_reminder_settings))
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
    # chat_id = message.chat.id
    # data = message.text
    # user = storage.get_user(chat_id=chat_id)
    # logger.info(f'Message data: {data}')

    # if user:
    #     # Clear keyboard
    #     bot.send_message(chat_id, text=error_messages['wrong_command'])
    #     statistics.add(action='Wrong command', storage=storage, tz=TZ_IRKUTSK)
    # else:
    #     bot.send_message(chat_id, text=error_messages['registration_not_finished'])
    #     statistics.add(action='Registration not finished', storage=storage, tz=TZ_IRKUTSK)
    pass


if __name__ == '__main__':
    bot.remove_webhook()
    logger.info('Bot started!')
    while True:
        try:
            bot.infinity_polling(none_stop=True)
        except Exception as e:
            logger.error(e)
            time.sleep(3)
