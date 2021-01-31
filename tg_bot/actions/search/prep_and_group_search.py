from functions.creating_schedule import full_schedule_in_str, full_schedule_in_str_prep
from functions.find_week import find_week
from functions.logger import logger
from tools import keyboards, schedule_processing, statistics
import json

# Глобальная переменная(словарь), которая хранит в себе 3 состояния
# (номер страницы; слово, которые находим; список соответствия для выхода по условию в стейте)
Condition_request = {}


def start_search(bot, message, storage, tz):
    data = message.chat.id
    message_id = message.message_id
    # ID пользователя
    chat_id = message.chat.id
    # Создаём ключ по значению ID пользователя
    Condition_request[chat_id] = []
    # Зарашиваем данные о пользователе из базы
    user = storage.get_user(chat_id=chat_id)
    # Условие для проверки наличия пользователя в базе

    if user:

        # Запуск стейта со значением SEARCH
        msg = bot.send_message(chat_id=chat_id, text='Введите название группы или фамилию преподавателя\n'
                                                     'Например: ИБб-18-1 или Иванов',
                               reply_markup=keyboards.make_keyboard_main_menu())

        bot.register_next_step_handler(msg, search, bot=bot, tz=tz, storage=storage)
        # bot.delete_message(message_id=message_id, chat_id=chat_id)

    else:

        bot.send_message(chat_id=chat_id, text='Привет\n')
        bot.send_message(chat_id=chat_id, text='Для начала пройдите небольшую регистрацию😉\n')
        bot.send_message(chat_id=chat_id, text='Выберите институт',
                         reply_markup=keyboards.make_inline_keyboard_choose_institute(storage.get_institutes()))


def search(message, bot, storage, tz, last_msg=None):
    """Регистрация преподавателя"""
    global Condition_request
    chat_id = message.chat.id
    message = message.text
    user = storage.get_user(chat_id=chat_id)
    all_found_groups = []
    all_found_prep = []
    page = 1

    if last_msg:
        message_id = last_msg.message_id
        bot.delete_message(message_id=message_id, chat_id=chat_id)

    if storage.get_search_list(message) or storage.get_search_list_prep(message):
        # Результат запроса по группам
        request_group = storage.get_search_list(message)
        # Результат запроса по преподам
        request_prep = storage.get_search_list_prep(message)
        # Циклы нужны для общего поиска. Здесь мы удаляем старые ключи в обоих реквестах и создаём один общий ключ, как для групп, так и для преподов
        for i in request_group:
            i['search'] = i.pop('name')
        for i in request_prep:
            i['search'] = i.pop('prep_short_name')
        # Записываем слово, которое ищем
        request_word = message
        # Склеиваем результаты двух запросов для общего поиска
        request = request_group + request_prep
        # Отправляем в функцию данные для создания клавиатуры
        keyboard = keyboards.make_keyboard_search_group(page, request)
        # Эти циклы записывают группы и преподов в нижнем регистре для удобной работы с ними
        for i in request_group:
            all_found_groups.append(i['search'].lower())
        for i in request_prep:
            all_found_prep.append(i['search'].lower())
        # Создаём общий список
        all_found_results = all_found_groups + all_found_prep
        # Формируем полный багаж для пользователя
        list_search = [page, request_word, all_found_results]
        # Записываем все данные под ключом пользователя
        Condition_request[chat_id] = list_search
        # Выводим результат поиска с клавиатурой (кливиатур формируется по поисковому запросу)
        bot.send_message(chat_id=chat_id, text='Результат поиска', reply_markup=keyboard)
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)

    else:
        msg = bot.send_message(chat_id=chat_id, text='Проверьте правильность ввода 😞')
        bot.register_next_step_handler(msg, search, bot=bot, storage=storage, tz=tz, last_msg=msg)

    return


def handler_buttons(bot, message, storage, tz):
    """Обрабатываем колбэк преподавателя"""
    global Condition_request
    chat_id = message.message.chat.id
    message_id = message.message.message_id
    data = json.loads(message.data)
    page = Condition_request[chat_id][0]
    request_word = Condition_request[chat_id][1]

    # Выходим из цикла поиска преподавателя по ФИО
    bot.clear_step_handler_by_chat_id(chat_id=chat_id)
    # Результат запроса по группам
    request_group = storage.get_search_list(request_word)
    # Результат запроса по преподам
    request_prep = storage.get_search_list_prep(request_word)
    # Циклы нужны для общего поиска. Здесь мы удаляем старые ключи в обоих реквестах и создаём один общий ключ, как для групп, так и для преподов
    for i in request_group:
        i['search'] = i.pop('name')
    for i in request_prep:
        i['search'] = i.pop('prep_short_name')
    # Склеиваем результаты двух запросов для общего поиска
    request = request_group + request_prep

    # Назад к институтам

    if data['main_menu'].lower() in Condition_request[chat_id][2]:
        bot.send_message(chat_id=chat_id, text='Выберите неделю',
                         reply_markup=keyboards.make_keyboard_choose_schedule())

    elif data['main_menu'] == 'back':
        bot.edit_message_text(message_id=message_id, chat_id=chat_id, text=f'Вы на странице {page - 1}',
                         reply_markup=keyboards.make_keyboard_search_group(page - 1, request))
        Condition_request[chat_id][0] -= 1
    elif data['main_menu'] == 'next':
        bot.edit_message_text(message_id=message_id, chat_id=chat_id, text=f'Вы на странице {page + 1}',
                         reply_markup=keyboards.make_keyboard_search_group(page + 1, request))
        Condition_request[chat_id][0] += 1
    # Регистрируем преподавателя по выбранной кнопке
    elif data['main_menu'] == 'main':
        bot.send_message(chat_id=chat_id, text='Основное меню',
                         reply_markup=keyboards.make_keyboard_start_menu())
    else:
        msg = bot.send_message(chat_id=chat_id, text='Проверьте правильность ввода 😞')
        bot.register_next_step_handler(msg, search, bot=bot, storage=storage, tz=tz, last_msg=msg)

        # bot.delete_message(message_id=message_id, chat_id=chat_id)
