from functions.creating_schedule import full_schedule_in_str, full_schedule_in_str_prep
from functions.find_week import find_week
from functions.logger import logger
from tg_bot.tools import keyboards, schedule_processing, statistics
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
    all_found_groups = []
    all_found_prep = []
    page = 0

    if last_msg:
        message_id = last_msg.message_id
        bot.delete_message(message_id=message_id, chat_id=chat_id)

    if storage.get_search_list(message) or storage.get_search_list_prep(message):
        # Результат запроса по группам
        request_group = storage.get_search_list(message)
        # Результат запроса по преподам
        request_prep = storage.get_search_list_prep(message)
        # Циклы нужны для общего поиска. Здесь мы удаляем старые ключи в обоих реквестах и создаём один общий ключ,
        # как для групп, так и для преподов
        for i in request_group:
            i['found_prep'] = i.pop('name')
        for i in request_prep:
            i['found_prep'] = i.pop('prep_short_name')
        # Записываем слово, которое ищем
        request_word = message
        # Склеиваем результаты двух запросов для общего поиска
        request = request_group + request_prep
        last_request = request[-1]
        # Отправляем в функцию данные для создания клавиатуры
        # Эти циклы записывают группы и преподов в нижнем регистре для удобной работы с ними
        for i in request_group:
            all_found_groups.append(i['found_prep'].lower())
        for i in request_prep:
            all_found_prep.append(i['found_prep'].lower())
        # Создаём общий список
        all_found_results = all_found_groups + all_found_prep
        # Формируем полный багаж для пользователя
        list_search = [page, request_word, all_found_results]
        # Записываем все данные под ключом пользователя
        Condition_request[chat_id] = list_search
        # Выводим результат поиска с клавиатурой (кливиатур формируется по поисковому запросу)
        if len(request) > 10:
            requests = request[:10 * (page + 1)]
            more_than_10 = True
            msg = bot.send_message(chat_id=chat_id, text='Результат поиска',
                                   reply_markup=keyboards.make_keyboard_search_group(last_request=last_request,
                                                                                     page=page,
                                                                                     more_than_10=more_than_10,
                                                                                     requests=requests))
            bot.register_next_step_handler(msg, search, bot=bot, storage=storage, tz=tz, last_msg=msg)

        else:
            msg = bot.send_message(chat_id=chat_id, text='Результат поиска',
                                   reply_markup=keyboards.make_keyboard_search_group(last_request=last_request,
                                                                                     page=page,
                                                                                     more_than_10=False,
                                                                                     requests=request))
            bot.register_next_step_handler(msg, search, bot=bot, storage=storage, tz=tz, last_msg=msg)

        # bot.clear_step_handler_by_chat_id(chat_id=chat_id)

    elif ('На текущую неделю' == message or 'На следующую неделю' == message):
        request_word = Condition_request[chat_id][1]
        request_group = storage.get_search_list(request_word)
        request_prep = storage.get_search_list_prep(request_word)
        # Если есть запрос для группы, то формируем расписание для группы, а если нет, то для препода
        if request_group:
            group = request_group[0]['name']
            schedule = storage.get_schedule(group=group)
        elif request_prep:
            group = request_prep[0]['prep']
            schedule = request_prep[0]
        if not schedule:
            bot.send_message(chat_id=chat_id, text='Расписание временно недоступно\nПопробуйте позже⏱')
            return

        schedule = schedule['schedule']
        week = find_week()

        # меняем неделю
        if message == 'На следующую неделю':
            week = 'odd' if week == 'even' else 'even'

        week_name = 'четная' if week == 'odd' else 'нечетная'
        if request_group:
            schedule_str = full_schedule_in_str(schedule, week=week)
        elif request_prep:
            schedule_str = full_schedule_in_str_prep(schedule, week=week)

        bot.send_message(chat_id=chat_id, text=f'Расписание {group}\n'
                                               f'Неделя: {week_name}',
                         reply_markup=keyboards.make_keyboard_start_menu())
        # Отправка расписания
        schedule_processing.sending_schedule_search(bot=bot, message=message, chat_id=chat_id,
                                                    schedule_str=schedule_str)

        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
    else:
        msg = bot.send_message(chat_id=chat_id, text='Проверьте правильность ввода 😞',
                               reply_markup=keyboards.make_keyboard_main_menu())
        bot.register_next_step_handler(msg, search, bot=bot, storage=storage, tz=tz, last_msg=msg)

    return


def handler_buttons(bot, message, storage, tz):
    """Обрабатываем колбэк преподавателя"""
    global Condition_request
    chat_id = message.message.chat.id
    message_id = message.message.message_id
    data = json.loads(message.data)

    if data['prep_list'] == 'main':

        bot.send_message(chat_id=chat_id, text='Основное меню',
                         reply_markup=keyboards.make_keyboard_start_menu())
        bot.delete_message(message_id=message_id, chat_id=chat_id)

        bot.clear_step_handler_by_chat_id(chat_id=chat_id)

        return

    if not Condition_request[chat_id] and len(Condition_request[chat_id]) != 0:
        Condition_request[chat_id][1] = ''


    page = Condition_request[chat_id][0]
    request_word = Condition_request[chat_id][1]

    # Выходим из цикла поиска преподавателя по ФИО
    bot.clear_step_handler_by_chat_id(chat_id=chat_id)
    # Результат запроса по группам
    request_group = storage.get_search_list(request_word)
    # Результат запроса по преподам
    request_prep = storage.get_search_list_prep(request_word)
    # Циклы нужны для общего поиска. Здесь мы удаляем старые ключи в обоих реквестах и создаём один общий ключ,
    # как для групп, так и для преподов
    for i in request_group:
        i['found_prep'] = i.pop('name')
    for i in request_prep:
        i['found_prep'] = i.pop('prep_short_name')
    # Склеиваем результаты двух запросов для общего поиска
    request = request_group + request_prep

    last_request = request[-1]

    # Назад к институтам
    if data['prep_list'].lower() in Condition_request[chat_id][2]:
        Condition_request[chat_id][1] = data['prep_list'].lower()
        msg = bot.send_message(chat_id=chat_id, text='Выберите неделю',
                               reply_markup=keyboards.make_keyboard_choose_schedule())
        bot.register_next_step_handler(msg, search, bot=bot, storage=storage, tz=tz, last_msg=msg)


    elif data['prep_list'] == 'back':
        more_than_10 = False
        if len(request) > 10:
            requests = request[10 * (page - 1):10 * page]
            more_than_10 = True

        if Condition_request[chat_id][0] - 1 == 0:
            bot.delete_message(message_id=message_id, chat_id=chat_id)
            msg = bot.send_message(chat_id=chat_id, text=f'Первая страница поиска:',
                                   reply_markup=keyboards.make_keyboard_search_group(last_request=last_request,
                                                                                     page=page - 1,
                                                                                     requests=requests,
                                                                                     more_than_10=more_than_10))
            bot.register_next_step_handler(msg, search, bot=bot, storage=storage, tz=tz, last_msg=msg)

        else:
            bot.edit_message_reply_markup(message_id=message_id, chat_id=chat_id,
                                          reply_markup=keyboards.make_keyboard_search_group(last_request=last_request,
                                                                                            page=page - 1,
                                                                                            requests=requests,
                                                                                            more_than_10=more_than_10))
        Condition_request[chat_id][0] -= 1

    elif data['prep_list'] == 'next':
        bot.delete_message(message_id=message_id, chat_id=chat_id)
        more_than_10 = False
        if len(request) > 10:
            requests = request[10 * (page + 1):10 * (page + 2)]
            more_than_10 = True
        msg = bot.send_message(chat_id=chat_id, text=f'Следующая страница',
                               reply_markup=keyboards.make_keyboard_search_group(last_request=last_request,
                                                                                 page=page + 1,
                                                                                 requests=requests,
                                                                                 more_than_10=more_than_10))
        bot.register_next_step_handler(msg, search, bot=bot, storage=storage, tz=tz, last_msg=msg)
        Condition_request[chat_id][0] += 1

    # Регистрируем преподавателя по выбранной кнопке

    else:
        msg = bot.send_message(chat_id=chat_id, text='Проверьте правильность ввода 😞',
                               reply_markup=keyboards.make_keyboard_main_menu())
        bot.register_next_step_handler(msg, search, bot=bot, storage=storage, tz=tz, last_msg=msg)
