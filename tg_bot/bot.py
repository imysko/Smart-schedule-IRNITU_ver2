import telebot

import pytz

import os
from time import sleep

from actions.main_menu import schedule
from functions.notifications import get_notifications_status
from functions.storage import MongodbService
from functions.logger import logger
from tools.keyboards import *
from functions.calculating_reminder_times import calculating_reminder_times

from flask import Flask, request

from tools import statistics

TOKEN = os.environ.get('TOKEN')
HOST_URL = os.environ.get('HOST_URL')

TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk')

bot = telebot.TeleBot(TOKEN, threaded=False)

storage = MongodbService().get_instance()

app = Flask(__name__)

content_schedule = ['Расписание 🗓', 'Ближайшая пара ⏱', 'Расписание на сегодня 🍏', 'На текущую неделю',
                    'На следующую неделю',
                    'Расписание на завтра 🍎', 'Следующая', 'Текущая']


# Обработка запросов от telegram
@app.route(f'/telegram-bot/{TOKEN}', methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return 'ok', 200


# Проверка работы сервера бота
@app.route('/telegram-bot/status')
def status():
    return 'Бот активен', 200


# ==================== Обработка команд ==================== #

# Команда /start
@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id

    # Проверяем есть пользователь в базе данных
    if storage.get_user(chat_id):
        storage.delete_user_or_userdata(chat_id)  # Удаляем пользвателя из базы данных

    bot.send_message(chat_id=chat_id, text='Привет!\n')
    bot.send_message(chat_id=chat_id, text='Для начала пройдите небольшую регистрацию😉\n'
                                           'Выберите институт',
                     reply_markup=make_inline_keyboard_choose_institute(storage.get_institutes()))

    statistics.add(action='start', storage=storage, tz=TZ_IRKUTSK)


# Команда /reg
@bot.message_handler(commands=['reg'])
def registration(message):
    chat_id = message.chat.id
    storage.delete_user_or_userdata(chat_id=chat_id)
    bot.send_message(chat_id=chat_id, text='Пройдите повторную регистрацию😉\n'
                                           'Выберите институт',
                     reply_markup=make_inline_keyboard_choose_institute(storage.get_institutes()))

    statistics.add(action='reg', storage=storage, tz=TZ_IRKUTSK)


# Команда /help
@bot.message_handler(commands=['help'])
def help(message):
    chat_id = message.chat.id
    bot.send_message(chat_id=chat_id, text='Список команд:\n'
                                           '/about - описание чат бота\n'
                                           '/authors - Список авторов \n'
                                           '/reg - повторная регистрация \n'
                                           '/map - карта университета \n')

    statistics.add(action='help', storage=storage, tz=TZ_IRKUTSK)


# Команда /map
@bot.message_handler(commands=['map'])
def map(message):
    chat_id = message.chat.id
    bot.send_photo(chat_id, (open('map.jpg', "rb")))
    # ФАЙЛОМ (РАБОТАЕТ)
    # map = open("map.jpg", "rb")
    # bot.send_document(chat_id, map)

    statistics.add(action='map', storage=storage, tz=TZ_IRKUTSK)


# Команда /about
@bot.message_handler(commands=['about'])
def about(message):
    chat_id = message.chat.id
    bot.send_message(chat_id=chat_id, parse_mode='HTML',
                     text='<b>О боте:\n</b>'
                          'Smart schedule IRNITU bot - это чат бот для просмотра расписания занятий в '
                          'Иркутском национальном исследовательском техническом университете\n\n'
                          '<b>Благодаря боту можно:\n</b>'
                          '- Узнать актуальное расписание\n'
                          '- Нажатием одной кнопки увидеть информацию о ближайшей паре\n'
                          '- Настроить гибкие уведомления с информацией из расписания, '
                          'которые будут приходить за определённое время до начала занятия')

    statistics.add(action='about', storage=storage, tz=TZ_IRKUTSK)


# Команда /authors
@bot.message_handler(commands=['authors'])
def authors(message):
    chat_id = message.chat.id
    bot.send_message(chat_id=chat_id, parse_mode='HTML',
                     text='<b>Авторы проекта:\n</b>'
                          '- Алексей @bolanebyla\n'
                          '- Султан @ace_sultan\n'
                          '- Александр @alexandrshen\n'
                          '- Владислав @TixoNNNAN\n'
                          '- Кирилл @ADAMYORT\n\n'
                          'По всем вопросом и предложениям пишите нам в личные сообщения. '
                          'Будем рады 😉\n'
                     )

    statistics.add(action='authors', storage=storage, tz=TZ_IRKUTSK)


# Handles all messages which text matches regexp.
@bot.message_handler(regexp='дароу', content_types=['text'])
def command_help(message):
    bot.send_message(message.chat.id, 'Did someone call for help?')


# words2 = ['save_notifications', 'del_notifications']
#
#
# @bot.callback_query_handler(func=lambda message: any(word in message.data for word in words2))
# def qwe(message):
#     print('asd')
#     chat_id = message.message.chat.id
#     bot.send_message(chat_id=chat_id,
#                      text='Работает!')


# ==================== Обработка Inline кнопок ==================== #
@bot.callback_query_handler(func=lambda call: True)
def handle_query(message):
    chat_id = message.message.chat.id
    message_id = message.message.message_id
    data = message.data

    logger.info(f'Inline button data: {data}')

    # После того как пользователь выбрал институт
    if 'institute' in data:
        data = json.loads(data)
        courses = storage.get_courses(data['institute'])

        institute = data['institute']

        storage.save_or_update_user(chat_id=chat_id,
                                    institute=data['institute'])  # Записываем в базу институт пользователя
        try:
            # Выводим сообщение со списком курсов
            bot.edit_message_text(message_id=message_id, chat_id=chat_id, text=f'Выберите курс',
                                  reply_markup=make_inline_keyboard_choose_courses(courses))
        except Exception as e:
            logger.exception(e)
            return

    # После того как пользователь выбрал курс или нажал кнопку назад при выборе курса
    elif 'course' in data:
        data = json.loads(data)

        # Если нажали кнопку назад
        if data['course'] == 'back':
            storage.delete_user_or_userdata(
                chat_id=chat_id)  # Удаляем информацию об институте пользователя из базы данных
            try:
                bot.edit_message_text(message_id=message_id, chat_id=chat_id,
                                      text='Выберите институт',
                                      reply_markup=make_inline_keyboard_choose_institute(storage.get_institutes()))
                return
            except Exception as e:
                logger.exception(e)
                return

        storage.save_or_update_user(chat_id=chat_id, course=data['course'])  # Записываем в базу курс пользователя
        user = storage.get_user(chat_id=chat_id)

        try:
            institute = user['institute']
            course = user['course']
            groups = storage.get_groups(institute=institute, course=course)
            # Выводим сообщение со списком групп
            bot.edit_message_text(message_id=message_id, chat_id=chat_id,
                                  text=f'Выберите группу',
                                  reply_markup=make_inline_keyboard_choose_groups(groups))
        except Exception as e:
            logger.exception(e)
            return

    # После того как пользователь выбрал группу или нажал кнопку назад при выборе группы
    elif 'group' in data:
        data = json.loads(data)

        # Если нажали кнопку назад
        if data['group'] == 'back':
            # Удаляем информацию о курсе пользователя из базы данных
            storage.delete_user_or_userdata(chat_id=chat_id,
                                            delete_only_course=True)
            try:
                institute = storage.get_user(chat_id=chat_id)['institute']
            except Exception as e:
                logger.exception(e)
                return
            courses = storage.get_courses(institute=institute)

            try:
                # Выводим сообщение со списком курсов
                bot.edit_message_text(message_id=message_id, chat_id=chat_id, text=f'Выберите курс',
                                      reply_markup=make_inline_keyboard_choose_courses(courses))
                return
            except Exception as e:
                logger.exception(e)
                return

        storage.save_or_update_user(chat_id=chat_id, group=data['group'])  # Записываем в базу группу пользователя

        try:
            # Удаляем меню регистрации
            bot.delete_message(message_id=message_id, chat_id=chat_id)
        except Exception as e:
            logger.exception(e)
            return

        bot.send_message(chat_id=chat_id,
                         text='Вы успешно зарегистрировались!😊\n\n'
                              'Для того чтобы пройти регистрацию повторно, воспользуйтесь командой /reg\n'
                              'Основные команды - /help',
                         reply_markup=make_keyboard_start_menu())

    elif 'notification_btn' in data:
        data = json.loads(data)
        if data['notification_btn'] == 'close':
            try:
                bot.delete_message(message_id=message_id, chat_id=chat_id)
                return
            except Exception as e:
                logger.exception(e)
                return
        time = data['notification_btn']

        try:
            bot.edit_message_text(message_id=message_id, chat_id=chat_id,
                                  text='Настройка напоминаний ⚙\n\n'
                                       'Укажите за сколько минут до начала пары должно приходить сообщение',
                                  reply_markup=make_inline_keyboard_set_notifications(time))
        except Exception as e:
            logger.exception(e)
            return

    elif 'del_notifications' in data:
        data = json.loads(data)
        time = data['del_notifications']
        if time == 0:
            return
        time -= 5

        if time < 0:
            time = 0

        try:
            bot.edit_message_reply_markup(message_id=message_id, chat_id=chat_id,
                                          reply_markup=make_inline_keyboard_set_notifications(time))
        except Exception as e:
            logger.exception(e)
            return

    elif 'add_notifications' in data:
        data = json.loads(data)
        time = data['add_notifications']
        time += 5

        try:
            bot.edit_message_reply_markup(message_id=message_id, chat_id=chat_id,
                                          reply_markup=make_inline_keyboard_set_notifications(time))
        except Exception as e:
            logger.exception(e)
            return

    elif 'save_notifications' in data:
        data = json.loads(data)
        time = data['save_notifications']

        group = storage.get_user(chat_id=chat_id)['group']

        schedule = storage.get_schedule(group=group)['schedule']
        if time > 0:
            reminders = calculating_reminder_times(schedule=schedule, time=int(time))
        else:
            reminders = []
        storage.save_or_update_user(chat_id=chat_id, notifications=time, reminders=reminders)

        try:
            bot.edit_message_text(message_id=message_id, chat_id=chat_id, text=get_notifications_status(time),
                                  reply_markup=make_inline_keyboard_notifications(time))
        except Exception as e:
            logger.exception(e)
            return

        statistics.add(action='save_notifications', storage=storage, tz=TZ_IRKUTSK)


# =============================================================


@bot.message_handler(func=lambda message: message.text in content_schedule, content_types=['text'])
def schedule_handler(message):
    """Расписание"""
    schedule.get_schedule(bot=bot, message=message, storage=storage, tz=TZ_IRKUTSK)


# ==================== Обработка текста ==================== #
@bot.message_handler(content_types=['text'])
def text(message):
    chat_id = message.chat.id
    data = message.text
    user = storage.get_user(chat_id=chat_id)
    logger.info(f'Message data: {data}')

    if 'Напоминание 📣' in data and user:
        time = user['notifications']
        if not time:
            time = 0
        bot.send_message(chat_id=chat_id, text=get_notifications_status(time),
                         reply_markup=make_inline_keyboard_notifications(time))

        statistics.add(action='Напоминания', storage=storage, tz=TZ_IRKUTSK)

    elif 'Основное меню' in data and user:
        bot.send_message(chat_id, text='Основное меню', reply_markup=make_keyboard_start_menu())

        statistics.add(action='Основное меню', storage=storage, tz=TZ_IRKUTSK)

    elif 'Авторы' == data and user:
        bot.send_message(chat_id, parse_mode='HTML', text='<b>Авторы проекта:\n</b>'
                                                          '- Алексей @bolanebyla\n'
                                                          '- Султан @ace_sultan\n'
                                                          '- Александр @alexandrshen\n'
                                                          '- Владислав @TixoNNNAN\n'
                                                          '- Кирилл @ADAMYORT\n\n'
                                                          'По всем вопросом и предложениям пишите нам в личные сообщения. '
                                                          'Будем рады 😉\n')

        statistics.add(action='Авторы', storage=storage, tz=TZ_IRKUTSK)

    elif 'Список команд' in data and user:
        bot.send_message(chat_id, text='Список команд:\n'
                                       'Авторы - список авторов \n'
                                       'Регистрация- повторная регистрация\n'
                                       'Карта - карта университета', reply_markup=make_keyboard_commands())

        statistics.add(action='Другое', storage=storage, tz=TZ_IRKUTSK)

    elif 'Другое ⚡' in data and user:
        bot.send_message(chat_id, text='Другое', reply_markup=make_keyboard_extra())

        statistics.add(action='Другое', storage=storage, tz=TZ_IRKUTSK)

    elif 'Регистрация' in data and user:
        bot.send_message(chat_id=chat_id, text='Пройдите повторную регистрацию😉\n'
                                               'Выберите институт',
                         reply_markup=make_inline_keyboard_choose_institute(storage.get_institutes()))

    elif 'Карта' in data and user:
        bot.send_message(chat_id=chat_id, text='Подождите, карта загружается...')
        bot.send_photo(chat_id, (open('map.jpg', "rb")))
        statistics.add(action='Карта', storage=storage, tz=TZ_IRKUTSK)

    else:
        if user:
            bot.send_message(chat_id, text='Я вас не понимаю 😞', reply_markup=make_keyboard_start_menu())
        else:
            bot.send_message(chat_id, text='Я вас не понимаю 😞')

        statistics.add(action='bullshit', storage=storage, tz=TZ_IRKUTSK)


if __name__ == '__main__':
    bot.skip_pending = True
    bot.remove_webhook()
    logger.info('Бот запущен локально')
    bot.polling(none_stop=True, interval=0)
else:
    bot.remove_webhook()
    sleep(1)
    bot.set_webhook(url=f'{HOST_URL}/telegram-bot/{TOKEN}')
