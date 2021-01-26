from functions.creating_schedule import full_schedule_in_str, full_schedule_in_str_prep, get_one_day_schedule_in_str, \
    get_next_day_schedule_in_str, get_one_day_schedule_in_str_prep, get_next_day_schedule_in_str_prep
from functions.calculating_reminder_times import calculating_reminder_times
from functions.near_lesson import get_near_lesson, get_now_lesson
from functions.storage import MongodbService
from vkbottle_types import BaseStateGroup
from functions.logger import logger
from functions.find_week import find_week
from keyboards import *
from vk_api import vk_api, VkUpload
import requests
import os
import pytz
from datetime import datetime
from vkbottle.bot import Bot, Message

from tools import schedule_processing
from actions import teacher_registration

TOKEN = os.environ.get('VK')

# Обьявление некоторых глбальных переменных


storage = MongodbService().get_instance()
bot = Bot(TOKEN)  # TOKEN

content_types = {
    'text': ['Расписание 🗓', 'Ближайшая пара ⏱', 'Расписание на сегодня 🍏', 'На текущую неделю',
             'На следующую неделю',
             'Расписание на завтра 🍎', 'Следующая', 'Текущая']}

сontent_commands = {'text': ['Начать', 'начать', 'Начало', 'start']}

content_map = {'text': ['map', 'Карта', 'карта', 'Map', 'Схема', 'схема']}

TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk')

authorize = vk_api.VkApi(token=TOKEN)
upload = VkUpload(authorize)
map_image = "map.jpg"

# Глобальные переменные
Condition_request = {}
prep_reg = {}
aud_list = {}


def get_notifications_status(time):
    """Статус напоминаний"""
    if not time or time == 0:
        notifications_status = 'Напоминания выключены ❌\n' \
                               'Воспользуйтесь настройками, чтобы включить'
    else:
        notifications_status = f'Напоминания включены ✅\n' \
                               f'Сообщение придёт за {time} мин до начала пары 😇'
    return notifications_status


# ==================== Создание основных клавиатур и кнопок ==================== #

def name_institutes(institutes=[]):
    """ Храним список всех институтов """

    list_institutes = []
    for i in institutes:
        name = i['name']
        list_institutes.append(name)
    return list_institutes


def name_courses(courses=[]):
    """ Храним список всех курсов """

    list_courses = []
    for i in courses:
        name = i['name']
        list_courses.append(name)
    return list_courses


def name_groups(groups=[]):
    """ Храним список всех групп """

    list_groups = []
    for i in groups:
        name = i['name']
        list_groups.append(name)
    return list_groups


def add_statistics(action: str):
    """Схоранение статистики"""

    date_now = datetime.now(TZ_IRKUTSK).strftime('%d.%m.%Y')
    time_now = datetime.now(TZ_IRKUTSK).strftime('%H:%M')
    storage.save_vk_statistics(action=action, date=date_now, time=time_now)


# ==================== ПОИСК ==================== #

class SuperStates(BaseStateGroup):
    SEARCH = 0
    PREP_REG = 1
    AUD_SEARCH = 2


@bot.on.message(state=SuperStates.SEARCH)  # Стейт для работы поиска
async def search(ans: Message):
    '''Стейт для работы поиска'''
    # Глобальная переменная(словарь), которая хранит в себе 3 состояния (номер страницы; слово, которые находим; список соответствия для выхода по условию в стейте)
    global Condition_request
    # Чат ID пользователя
    chat_id = ans.from_id
    # Данные ввода
    data = ans.text
    # Соответствия по группам
    all_found_groups = []
    # Соответствия для преподов
    all_found_prep = []
    # Задаём состояние для первой страницы
    page = 1
    # Логирование для информации в рил-тайм
    logger.info(f'Inline button data: {data}')
    # Условие для первичного входа пользователя
    if (storage.get_search_list(ans.text) or storage.get_search_list_prep(ans.text)) and Condition_request[
        chat_id] == []:
        # Результат запроса по группам
        request_group = storage.get_search_list(ans.text)
        # Результат запроса по преподам
        request_prep = storage.get_search_list_prep(ans.text)
        # Циклы нужны для общего поиска. Здесь мы удаляем старые ключи в обоих реквестах и создаём один общий ключ, как для групп, так и для преподов
        for i in request_group:
            i['search'] = i.pop('name')
        for i in request_prep:
            i['search'] = i.pop('prep_short_name')
        # Записываем слово, которое ищем
        request_word = ans.text
        # Склеиваем результаты двух запросов для общего поиска
        request = request_group + request_prep
        # Отправляем в функцию данные для создания клавиатуры
        keyboard = make_keyboard_search_group(page, request)
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
        await ans.answer("Результат поиска", keyboard=keyboard)

    # Здесь уловия для выхода в основное меню
    elif ans.text == "Основное меню":
        del Condition_request[ans.from_id]
        await ans.answer("Основное меню", keyboard=make_keyboard_start_menu())
        await bot.state_dispenser.delete(ans.peer_id)

    # Здесь уловие для слова "Дальше"
    elif ans.text == "Дальше":
        page = Condition_request[ans.from_id][0]
        Condition_request[ans.from_id][0] += 1
        request_word = Condition_request[ans.from_id][1]
        request_group = storage.get_search_list(request_word)
        request_prep = storage.get_search_list_prep(request_word)
        for i in request_group:
            i['search'] = i.pop('name')
        for i in request_prep:
            i['search'] = i.pop('prep_short_name')
        request = request_group + request_prep
        request = request[26 * page:]
        keyboard = make_keyboard_search_group(page + 1, request)
        await ans.answer(f"Страница {page + 1}", keyboard=keyboard)

    # По аналогии со словом "<==Назад", только обратный процесс
    elif ans.text == "<==Назад":
        Condition_request[ans.from_id][0] -= 1
        page = Condition_request[ans.from_id][0]
        request_word = Condition_request[ans.from_id][1]
        request_group = storage.get_search_list(request_word)
        request_prep = storage.get_search_list_prep(request_word)
        for i in request_group:
            i['search'] = i.pop('name')
        for i in request_prep:
            i['search'] = i.pop('prep_short_name')
        request = request_group + request_prep
        request = request[26 * (page - 1):]
        keyboard = make_keyboard_search_group(page, request)
        await ans.answer(f"Страница {page}", keyboard=keyboard)

    # Условие для вывода расписания для группы и преподавателя по неделям
    elif ('На текущую неделю' == data or 'На следующую неделю' == data):
        group = Condition_request[ans.from_id][1]
        request_word = Condition_request[ans.from_id][1]
        request_group = storage.get_search_list(request_word)
        request_prep = storage.get_search_list_prep(request_word)
        # Если есть запрос для группы, то формируем расписание для группы, а если нет, то для препода
        if request_group:
            schedule = storage.get_schedule(group=group)
        elif request_prep:
            schedule = request_prep[0]
        if schedule['schedule'] == []:
            await ans.answer('Расписание временно недоступно\nПопробуйте позже⏱')
            add_statistics(action=data)
            return

        schedule = schedule['schedule']
        week = find_week()

        # меняем неделю
        if data == 'На следующую неделю':
            week = 'odd' if week == 'even' else 'even'

        week_name = 'четная' if week == 'odd' else 'нечетная'
        if request_group:
            schedule_str = full_schedule_in_str(schedule, week=week)
        elif request_prep:
            schedule_str = full_schedule_in_str_prep(schedule, week=week)

        await ans.answer(f'Расписание {group}\n'
                         f'Неделя: {week_name}', keyboard=make_keyboard_start_menu())
        # Отправка расписания
        await schedule_processing.sending_schedule(ans=ans, schedule_str=schedule_str)

        await bot.state_dispenser.delete(ans.peer_id)

    # Условия для завершения поиска, тобишь окончательный выбор пользователя
    elif (storage.get_search_list(ans.text) or storage.get_search_list_prep(ans.text)) and ans.text.lower() in \
            (i for i in Condition_request[ans.from_id][2]):
        choose = ans.text
        Condition_request[ans.from_id][1] = choose
        request_word = Condition_request[ans.from_id][1]
        request_group = storage.get_search_list(request_word)
        request_prep = storage.get_search_list_prep(request_word)
        for i in request_group:
            i['search'] = i.pop('name')
        for i in request_prep:
            i['search'] = i.pop('prep_short_name')
        if request_group:
            await ans.answer(f"Выберите неделю для группы {choose}", keyboard=make_keyboard_choose_schedule())
        elif request_prep:
            await ans.answer(f"Выберите неделю для преподавателя {request_prep[0]['prep']}",
                             keyboard=make_keyboard_choose_schedule())
        else:
            return
    # Общее исключения для разных случаем, которые могу сломать бота. (Практически копия первого IF)
    else:
        if Condition_request[ans.from_id] and storage.get_search_list(ans.text) or storage.get_search_list_prep(
                ans.text):
            request_group = storage.get_search_list(ans.text)
            request_prep = storage.get_search_list_prep(ans.text)
            for i in request_group:
                i['search'] = i.pop('name')
            for i in request_prep:
                i['search'] = i.pop('prep_short_name')
            request_word = ans.text
            request = request_group + request_prep
            keyboard = make_keyboard_search_group(page, request)
            for i in request_group:
                all_found_groups.append(i['search'].lower())
            for i in request_prep:
                all_found_prep.append(i['search'].lower())
            all_found_results = all_found_groups + all_found_prep
            list_search = [page, request_word, all_found_results]
            Condition_request[chat_id] = list_search
            await ans.answer("Результат поиска", keyboard=keyboard)

        else:
            if len(Condition_request[chat_id]) == 3:
                Condition_request[chat_id][1] = ''
                await ans.answer('Поиск не дал результатов 😕')
                return
            else:
                await ans.answer('Поиск не дал результатов 😕')
                return


@bot.on.message(text="Преподаватель")  # Вхождение в стейт регистрации преподавателей
async def start_prep_reg(ans: Message):
    await teacher_registration.start_prep_reg(bot=bot, ans=ans, SuperStates=SuperStates, storage=storage)


@bot.on.message(text="Аудитории")  # Вхождение в стейт поиска аудитории
async def start_aud_search(ans: Message):
    """Вхождение в стейт поиска аудитории"""
    global aud_list
    chat_id = ans.from_id
    aud_list[chat_id] = []
    await ans.answer('Введите интересующую аудитрию\n'
                     'Например: Ж-317, или Ж317', keyboard=make_keyboard_main_menu())

    await bot.state_dispenser.set(ans.peer_id, SuperStates.AUD_SEARCH)


@bot.on.message(state=SuperStates.AUD_SEARCH)  # Стейт поиска по аудиториям
async def aud_search(ans: Message):
    """Стейт поиска по аудиториям"""
    global aud_list
    # Чат ID пользователя
    chat_id = ans.from_id
    # Данные ввода
    data = ans.text
    # Соответствия по группам
    all_found_aud = []
    # Соответствия для преподов
    # Задаём состояние для первой страницы
    page = 1
    prep_list = []

    if not storage.get_schedule_aud(data) and len((ans.text).replace(' ', '')) < 15:
        # Отправляем запросы в базу посимвольно
        for item in data:
            # Получаем все результаты запроса на каждый символ
            request_item_all = storage.get_schedule_aud(item)
            # Проходим по каждому результату запроса одного символа
            for i in range(len(request_item_all)):
                # Обращаемся к результатам у которых есть ключ "aud"
                request_item = request_item_all[i]['aud']
                # Записывем все совпадения (Значения ключа "aud")
                prep_list.append(request_item)
                request_item = []

            request_item_all = []

        # Выделение наиболее повторяющихся элементов(а). Фактически результат запроса пользователя.
        qty_most_common = 0
        prep_list_set = set(prep_list)
        for item in prep_list_set:
            qty = prep_list.count(item)
            if qty > qty_most_common:
                qty_most_common = qty
                # Переменная с результатом сортировки
            if item.replace('-', '').lower() in ans.text.replace(' ', '').lower():
                data = item

    # Условие для первичного входа пользователя
    if storage.get_schedule_aud(data) and aud_list[chat_id] == []:
        # Результат запроса по аудам
        request_aud = storage.get_schedule_aud(data)
        # Циклы нужны для общего поиска. Здесь мы удаляем старые ключи в обоих реквестах и создаём один общий ключ, как для групп, так и для преподов
        for i in request_aud:
            i['search'] = i.pop('aud')
        # Записываем слово, которое ищем
        request_word = data
        # Отправляем в функцию данные для создания клавиатуры
        keyboard = make_keyboard_search_group(page, request_aud)
        # Эти циклы записывают группы и преподов в нижнем регистре для удобной работы с ними
        for i in request_aud:
            all_found_aud.append(i['search'].lower())
        # Формируем полный багаж для пользователя
        list_search = [page, request_word, all_found_aud]
        # Записываем все данные под ключом пользователя
        aud_list[chat_id] = list_search
        # Выводим результат поиска с клавиатурой (кливиатур формируется по поисковому запросу)
        await ans.answer("Результат поиска", keyboard=keyboard)



    # Здесь уловия для выхода в основное меню
    elif data == "Основное меню":
        del aud_list[ans.from_id]
        await ans.answer("Основное меню", keyboard=make_keyboard_start_menu())
        await bot.state_dispenser.delete(ans.peer_id)

    # Здесь уловие для слова "Дальше"
    elif data == "Дальше":
        page = aud_list[ans.from_id][0]
        aud_list[ans.from_id][0] += 1
        request_word = aud_list[ans.from_id][1]
        request_aud = storage.get_schedule_aud(request_word)
        for i in request_aud:
            i['search'] = i.pop('aud')
        request_aud = request_aud[26 * page:]
        keyboard = make_keyboard_search_group(page + 1, request_aud)
        await ans.answer(f"Страница {page + 1}", keyboard=keyboard)

    # По аналогии со словом "<==Назад", только обратный процесс
    elif data == "<==Назад":
        aud_list[ans.from_id][0] -= 1
        page = aud_list[ans.from_id][0]
        request_word = aud_list[ans.from_id][1]
        request_aud = storage.get_schedule_aud(request_word)
        for i in request_aud:
            i['search'] = i.pop('aud')
        request_aud = request_aud[26 * (page - 1):]
        keyboard = make_keyboard_search_group(page, request_aud)
        await ans.answer(f"Страница {page}", keyboard=keyboard)

    # Условие для вывода расписания для группы и преподавателя по неделям
    elif ('На текущую неделю' == data or 'На следующую неделю' == data):
        group = aud_list[ans.from_id][1]
        request_word = aud_list[ans.from_id][1]
        request_aud = storage.get_schedule_aud(request_word)
        # Если есть запрос для группы, то формируем расписание для группы, а если нет, то для препода
        schedule = request_aud[0]

        if schedule['schedule'] == []:
            await schedule_processing.sending_schedule_is_not_available(ans=ans)
            add_statistics(action=data)
            return

        schedule = schedule['schedule']
        week = find_week()

        # меняем неделю
        if data == 'На следующую неделю':
            week = 'odd' if week == 'even' else 'even'

        week_name = 'четная' if week == 'odd' else 'нечетная'

        aud = request_word

        schedule_str = full_schedule_in_str_prep(schedule, week=week, aud=aud)

        await ans.answer(f'Расписание {group}\n'
                         f'Неделя: {week_name}', keyboard=make_keyboard_start_menu())

        # Отправка расписания
        await schedule_processing.sending_schedule(ans=ans, schedule_str=schedule_str)

        await bot.state_dispenser.delete(ans.peer_id)

    # Условия для завершения поиска, тобишь окончательный выбор пользователя
    elif storage.get_schedule_aud(data) and data.lower() in (i for i in aud_list[ans.from_id][2]):
        choose = data
        aud_list[ans.from_id][1] = choose
        request_word = aud_list[ans.from_id][1]
        request_aud = storage.get_schedule_aud(request_word)
        for i in request_aud:
            i['search'] = i.pop('aud')

        await ans.answer(f"Выберите неделю для аудитории {choose}", keyboard=make_keyboard_choose_schedule())

        return
    # Общее исключения для разных случаем, которые могу сломать бота. (Практически копия первого IF)
    else:
        if aud_list[ans.from_id] and storage.get_schedule_aud(data):

            # Результат запроса по аудам
            request_aud = storage.get_schedule_aud(data)
            # Циклы нужны для общего поиска. Здесь мы удаляем старые ключи в обоих реквестах и создаём один общий ключ, как для групп, так и для преподов
            for i in request_aud:
                i['search'] = i.pop('aud')
            # Записываем слово, которое ищем
            request_word = data
            # Отправляем в функцию данные для создания клавиатуры
            keyboard = make_keyboard_search_group(page, request_aud)
            # Эти циклы записывают группы и преподов в нижнем регистре для удобной работы с ними
            for i in request_aud:
                all_found_aud.append(i['search'].lower())
            # Формируем полный багаж для пользователя
            list_search = [page, request_word, all_found_aud]
            # Записываем все данные под ключом пользователя
            aud_list[chat_id] = list_search
            # Выводим результат поиска с клавиатурой (кливиатур формируется по поисковому запросу)
            await ans.answer("Результат поиска", keyboard=keyboard)

        else:
            # Проверяем есть ли результат на запрос с "-"
            if len(aud_list[chat_id]) == 3:
                aud_list[chat_id][1] = ''
                await ans.answer('Поиск не дал результатов 😕', keyboard=make_keyboard_main_menu())
                return
            else:
                await ans.answer('Поиск не дал результатов 😕', keyboard=make_keyboard_main_menu())
                return


@bot.on.message(state=SuperStates.PREP_REG)  # Стейт регистрации преподавателей
async def reg_prep(ans: Message):
    """Стейт регистрации преподавателей"""
    await teacher_registration.reg_prep(bot=bot, ans=ans, storage=storage)


# ==================== Обработка команд ==================== #
# Входим в стейт по кодовому слову "Поиск"
@bot.on.message(text="Группы и преподаватели")  # Вхождение в стейт поиска
async def die_handler(ans: Message):
    """Вхождение в стейт поиска"""
    # глобальная переменная(словарь), которая хранит в себе 3 состояния (номер страницы; слово, которые находим; список соответствия для выхода по условию в стейте)
    global Condition_request
    # ID пользователя
    chat_id = ans.from_id
    # Создаём ключ по значению ID пользователя
    Condition_request[chat_id] = []
    # Зарашиваем данные о пользователе из базы
    user = storage.get_vk_user(chat_id=chat_id)
    # Условие для проверки наличия пользователя в базе
    if user:
        # Запуск стейта со значением SEARCH
        await bot.state_dispenser.set(ans.peer_id, SuperStates.SEARCH)
        await ans.answer('Введите название группы или фамилию преподавателя\n'
                         'Например: ИБб-18-1 или Иванов', keyboard=make_keyboard_main_menu())
    else:
        await ans.answer('Привет\n')
        await ans.answer('Для начала пройдите небольшую регистрацию😉\n')
        await ans.answer('Выберите институт.', keyboard=make_keyboard_institutes(storage.get_institutes()))


# Команда start
@bot.on.message(text=сontent_commands['text'])
async def start_message(ans: Message):
    chat_id = ans.from_id

    # Проверяем есть пользователь в базе данных
    if storage.get_vk_user(chat_id):
        storage.delete_vk_user_or_userdata(chat_id)  # Удаляем пользвателя из базы данных
    await ans.answer('Привет\n')
    await ans.answer('Для начала пройдите небольшую регистрацию😉\n')
    await ans.answer('Выберите институт.', keyboard=make_keyboard_institutes(storage.get_institutes()))

    add_statistics(action='start')


# Команда Регистрация
@bot.on.message(text='Регистрация')
async def registration(ans: Message):
    chat_id = ans.from_id
    # Проверяем есть пользователь в базе данных
    if storage.get_vk_user(chat_id):
        storage.delete_vk_user_or_userdata(chat_id)  # Удаляем пользвателя из базы данных
    await ans.answer('Повторная регистрация😉\n')
    await ans.answer('Выберите институт.', keyboard=make_keyboard_institutes(storage.get_institutes()))

    add_statistics(action='reg')


# Команда Карта
@bot.on.message(text=content_map['text'])
async def map(ans: Message):
    chat_id = ans.from_id
    await ans.answer('Подождите, карта загружается...', keyboard=make_keyboard_start_menu())
    server = authorize.method("photos.getMessagesUploadServer")
    b = requests.post(server['upload_url'], files={'photo': open('map.jpg', 'rb')}).json()
    c = authorize.method('photos.saveMessagesPhoto', {'photo': b['photo'], 'server': b['server'], 'hash': b['hash']})[0]
    authorize.method("messages.send",
                     {"peer_id": chat_id, "attachment": f'photo{c["owner_id"]}_{c["id"]}', 'random_id': 0})

    add_statistics(action='map')


# Команда Авторы
@bot.on.message(text='Авторы')
async def authors(ans: Message):
    chat_id = ans.from_id
    await ans.answer('Авторы проекта:\n'
                     '-[id132677094|Алексей]\n'
                     '-[id128784852|Султан]\n'
                     '-[id169584462|Александр] \n'
                     '-[id135615548|Владислав]\n'
                     '-[id502898628|Кирилл]\n\n'
                     'По всем вопросом и предложениям пишите нам в личные сообщения. '
                     'Будем рады 😉\n', keyboard=make_keyboard_start_menu()
                     )

    add_statistics(action='authors')


@bot.on.message(text=content_types['text'])
async def scheduler(ans: Message):
    chat_id = ans.from_id
    data = ans.text
    user = storage.get_vk_user(chat_id=chat_id)

    if 'Расписание 🗓' == data and user.get('group'):
        await ans.answer('Выберите период\n', keyboard=make_keyboard_choose_schedule())
        add_statistics(action='Расписание')

    if ('На текущую неделю' == data or 'На следующую неделю' == data) and user.get('group'):
        # Если курс нуль, тогда это преподаватель
        if storage.get_vk_user(chat_id=chat_id)['course'] != 'None':
            group = storage.get_vk_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule(group=group)
        elif storage.get_vk_user(chat_id=chat_id)['course'] == 'None':
            group = storage.get_vk_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule_prep(group=group)
        if schedule['schedule'] == []:
            await ans.answer('Расписание временно недоступно\nПопробуйте позже⏱')
            add_statistics(action=data)
            return

        schedule = schedule['schedule']
        week = find_week()

        # меняем неделю
        if data == 'На следующую неделю':
            week = 'odd' if week == 'even' else 'even'

        week_name = 'четная' if week == 'odd' else 'нечетная'

        if storage.get_vk_user(chat_id=chat_id)['course'] != 'None':
            schedule_str = full_schedule_in_str(schedule, week=week)
        elif storage.get_vk_user(chat_id=chat_id)['course'] == 'None':
            schedule_str = full_schedule_in_str_prep(schedule, week=week)

        await ans.answer(f'Расписание {group}\n'
                         f'Неделя: {week_name}', keyboard=make_keyboard_start_menu())

        # Отправка расписания
        await schedule_processing.sending_schedule(ans=ans, schedule_str=schedule_str)

        add_statistics(action=data)



    elif 'Расписание на сегодня 🍏' == data and user.get('group'):
        # Если курс нуль, тогда это преподаватель
        if storage.get_vk_user(chat_id=chat_id)['course'] != 'None':
            group = storage.get_vk_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule(group=group)
        elif storage.get_vk_user(chat_id=chat_id)['course'] == 'None':
            group = storage.get_vk_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule_prep(group=group)
        if not schedule:
            await ans.answer('Расписание временно недоступно🚫😣\n'
                             'Попробуйте позже⏱', keyboard=make_keyboard_start_menu())
            add_statistics(action='Расписание на сегодня')
            return
        schedule = schedule['schedule']
        week = find_week()
        # Если курс нуль, тогда это преподаватель
        if storage.get_vk_user(chat_id=chat_id)['course'] != 'None':
            schedule_one_day = get_one_day_schedule_in_str(schedule=schedule, week=week)
        elif storage.get_vk_user(chat_id=chat_id)['course'] == 'None':
            schedule_one_day = get_one_day_schedule_in_str_prep(schedule=schedule, week=week)
        if not schedule_one_day:
            await ans.answer('Сегодня пар нет 😎')
            return
        await ans.answer(f'{schedule_one_day}')
        add_statistics(action='Расписание на сегодня')

    elif 'Расписание на завтра 🍎' == data and user.get('group'):
        # Если курс нуль, тогда это преподаватель
        if storage.get_vk_user(chat_id=chat_id)['course'] != 'None':
            group = storage.get_vk_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule(group=group)
        elif storage.get_vk_user(chat_id=chat_id)['course'] == 'None':
            group = storage.get_vk_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule_prep(group=group)
        if not schedule:
            await ans.answer('Расписание временно недоступно🚫😣\n'
                             'Попробуйте позже⏱', keyboard=make_keyboard_start_menu())
            add_statistics(action='Расписание на завтра')
            return
        schedule = schedule['schedule']
        week = find_week()
        if datetime.today().isoweekday() == 7:
            if week == 'odd':
                week = 'even'
            elif week == 'even':
                week = 'odd'
            else:
                week = 'all'

        if storage.get_vk_user(chat_id=chat_id)['course'] != 'None':
            schedule_next_day = get_next_day_schedule_in_str(schedule=schedule, week=week)
        elif storage.get_vk_user(chat_id=chat_id)['course'] == 'None':
            schedule_next_day = get_next_day_schedule_in_str_prep(schedule=schedule, week=week)

        if not schedule_next_day:
            await ans.answer('Завтра пар нет 😎')
            return
        await ans.answer(f'{schedule_next_day}')
        add_statistics(action='Расписание на завтра')

    elif 'Ближайшая пара ⏱' in data and user.get('group'):
        await ans.answer('Ближайшая пара', keyboard=make_keyboard_nearlesson())
        add_statistics(action='Ближайшая пара')
        return


    elif 'Текущая' in data and user.get('group'):
        if storage.get_vk_user(chat_id=chat_id)['course'] != 'None':
            group = storage.get_vk_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule(group=group)
        elif storage.get_vk_user(chat_id=chat_id)['course'] == 'None':
            group = storage.get_vk_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule_prep(group=group)
        if not schedule:
            await ans.answer('Расписание временно недоступно🚫😣\n'
                             'Попробуйте позже⏱', keyboard=make_keyboard_start_menu())
            add_statistics(action='Текущая')
            return
        schedule = schedule['schedule']
        week = find_week()

        now_lessons = get_now_lesson(schedule=schedule, week=week)

        # если пар нет
        if not now_lessons:
            await ans.answer('Сейчас пары нет, можете отдохнуть)', keyboard=make_keyboard_start_menu())
            add_statistics(action='Текущая')
            return

        now_lessons_str = ''

        if storage.get_vk_user(chat_id=chat_id)['course'] != 'None':
            for near_lesson in now_lessons:
                name = near_lesson['name']
                if name == 'свободно':
                    await ans.answer('Сейчас пары нет, можете отдохнуть)', keyboard=make_keyboard_start_menu())
                    return
                now_lessons_str += '-------------------------------------------\n'
                aud = near_lesson['aud']
                if aud:
                    aud = f'Аудитория: {aud}\n'
                time = near_lesson['time']
                info = near_lesson['info'].replace(",", "")
                prep = near_lesson['prep']

                now_lessons_str += f'{time}\n' \
                                   f'{aud}' \
                                   f'👉{name}\n' \
                                   f'{info} {prep}\n'
            now_lessons_str += '-------------------------------------------\n'

        elif storage.get_vk_user(chat_id=chat_id)['course'] == 'None':
            for near_lesson in now_lessons:
                name = near_lesson['name']
                if name == 'свободно':
                    await ans.answer('Сейчас пары нет, можете отдохнуть)', keyboard=make_keyboard_start_menu())
                    return
                now_lessons_str += '-------------------------------------------\n'
                aud = near_lesson['aud']
                if aud:
                    aud = f'Аудитория: {aud}\n'
                time = near_lesson['time']
                info = near_lesson['info'].replace(",", "")
                groups = ', '.join(near_lesson['groups'])

                now_lessons_str += f'{time}\n' \
                                   f'{aud}' \
                                   f'👉{name}\n' \
                                   f'{info} {groups}\n'
            now_lessons_str += '-------------------------------------------\n'

        await ans.answer(f'🧠Текущая пара🧠\n'f'{now_lessons_str}', keyboard=make_keyboard_start_menu())

        add_statistics(action='Текущая')

    elif 'Следующая' in data and user.get('group'):
        if storage.get_vk_user(chat_id=chat_id)['course'] != 'None':
            group = storage.get_vk_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule(group=group)
        elif storage.get_vk_user(chat_id=chat_id)['course'] == 'None':
            group = storage.get_vk_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule_prep(group=group)
        if not schedule:
            await ans.answer('Расписание временно недоступно🚫😣\n'
                             'Попробуйте позже⏱', keyboard=make_keyboard_start_menu())
            add_statistics(action='Следующая')
            return
        schedule = schedule['schedule']
        week = find_week()

        near_lessons = get_near_lesson(schedule=schedule, week=week)

        # если пар нет
        if not near_lessons:
            await ans.answer('Сегодня больше пар нет 😎', keyboard=make_keyboard_start_menu())
            add_statistics(action='Следующая')
            return

        near_lessons_str = ''

        if storage.get_vk_user(chat_id=chat_id)['course'] != 'None':
            for near_lesson in near_lessons:
                name = near_lesson['name']
                if name == 'свободно':
                    await ans.answer('Сегодня больше пар нет 😎', keyboard=make_keyboard_start_menu())
                    return
                near_lessons_str += '-------------------------------------------\n'
                aud = near_lesson['aud']
                if aud:
                    aud = f'Аудитория: {aud}\n'
                time = near_lesson['time']

                info = near_lesson['info'].replace(",", "")
                prep = near_lesson['prep']

                near_lessons_str += f'{time}\n' \
                                    f'{aud}' \
                                    f'👉{name}\n' \
                                    f'{info} {prep}\n'

            near_lessons_str += '-------------------------------------------\n'
            await ans.answer(f'🧠Ближайшая пара🧠\n'f'{near_lessons_str}', keyboard=make_keyboard_start_menu())

        elif storage.get_vk_user(chat_id=chat_id)['course'] == 'None':
            for near_lesson in near_lessons:
                name = near_lesson['name']
                if name == 'свободно':
                    await ans.answer('Сегодня больше пар нет 😎', keyboard=make_keyboard_start_menu())
                    return
                near_lessons_str += '-------------------------------------------\n'
                aud = near_lesson['aud']
                if aud:
                    aud = f'Аудитория: {aud}\n'
                time = near_lesson['time']
                info = near_lesson['info'].replace(",", "")
                groups = ', '.join(near_lesson['groups'])

                near_lessons_str += f'{time}\n' \
                                    f'{aud}' \
                                    f'👉{name}\n' \
                                    f'{info} {groups}\n'
            near_lessons_str += '-------------------------------------------\n'
            await ans.answer(f'🧠Ближайшая пара🧠\n'f'{near_lessons_str}', keyboard=make_keyboard_start_menu())

        add_statistics(action='Следующая')


@bot.on.message()
async def wrapper(ans: Message):
    '''Регистрация пользователя'''
    chat_id = ans.from_id
    message_inst = ans.text
    message = ans.text
    user = storage.get_vk_user(chat_id)
    print(user)

    # Сохраняет в месседж полное название универ для корректного сравнения
    institutes = name_institutes(storage.get_institutes())
    for institute in institutes:
        if len(message_inst) > 5:
            if message_inst[:-5] in institute:
                message_inst = institute

    # Если пользователя нет в базе данных
    if not user:
        institutes = name_institutes(storage.get_institutes())
        # Смотрим выбрал ли пользователь институт
        if message_inst in institutes:
            # Если да, то записываем в бд
            storage.save_or_update_vk_user(chat_id=chat_id, institute=message_inst)
            await ans.answer(f'Вы выбрали: {message_inst}\n')
            await ans.answer('Выберите курс.',
                             keyboard=make_keyboard_choose_course_vk(storage.get_courses(message_inst)))

    # Если нажал кнопку Назад к институтам
    elif message == "Назад к институтам" and not 'course' in user.keys():
        await ans.answer('Выберите институт.', keyboard=make_keyboard_institutes(storage.get_institutes()))
        storage.delete_vk_user_or_userdata(chat_id=chat_id)
        return

    # Если нажал кнопку Назад к курсам
    elif message == "Назад к курсам" and not 'group' in user.keys():

        await ans.answer('Выберите курс.', keyboard=make_keyboard_choose_course_vk(
            storage.get_courses(storage.get_vk_user(chat_id=chat_id)['institute'])))
        storage.delete_vk_user_or_userdata(chat_id=chat_id, delete_only_course=True)
        return

    # Регистрация после выбора института
    elif not 'course' in user.keys():
        institute = user['institute']
        course = storage.get_courses(institute)
        # Если нажал кнопку курса
        if message in name_courses(course):
            # Записываем в базу данных выбранный курс
            storage.save_or_update_vk_user(chat_id=chat_id, course=message)
            groups = storage.get_groups(institute=institute, course=message)
            groups = name_groups(groups)
            await ans.answer(f'Вы выбрали: {message}\n')
            await ans.answer('Выберите группу.', keyboard=make_keyboard_choose_group_vk(groups))
            return
        else:
            await ans.answer('Не огорчай нас, мы же не просто так старались над клавиатурой 😼👇🏻')
        return

    # Регистрация после выбора курса
    elif not 'group' in user.keys():
        institute = user['institute']
        course = user['course']
        groups = storage.get_groups(institute=institute, course=course)
        groups = name_groups(groups)
        # Если нажал кнопку группы
        if message in groups:
            # Записываем в базу данных выбранную группу
            storage.save_or_update_vk_user(chat_id=chat_id, group=message)
            await ans.answer('Вы успешно зарегистрировались!😊\n\n'
                             'Для того чтобы пройти регистрацию повторно, напишите сообщение "Регистрация"\n'
                             , keyboard=make_keyboard_start_menu())
        else:
            if message == "Далее":
                await ans.answer('Выберите группу.', keyboard=make_keyboard_choose_group_vk_page_2(groups))
            elif message == "Назад":
                await ans.answer('Выберите группу.', keyboard=make_keyboard_choose_group_vk(groups))
            else:
                await ans.answer('Я очень сомневаюсь, что твоей группы нет в списке ниже 😉')
        return

    elif 'Напоминание 📣' in message and user.get('group'):
        time = user['notifications']
        # Проверяем стату напоминания
        if not time:
            time = 0
        await ans.answer(f'{get_notifications_status(time)}', keyboard=make_inline_keyboard_notifications())

        add_statistics(action='Напоминание')

    elif 'Настройки' in message and user.get('group'):
        time = user['notifications']
        await ans.answer('Настройка напоминаний ⚙\n\n'
                         'Укажите за сколько минут до начала пары должно приходить сообщение',
                         keyboard=make_inline_keyboard_set_notifications(time))
        add_statistics(action='Настройки')

    elif '-' == message:
        time = user['notifications']
        if time == 0:
            await ans.answer('Хочешь уйти в минус?', keyboard=make_inline_keyboard_set_notifications(time))
            return
        time -= 5
        # Отнимаем и проверяем на положительность
        if time <= 0:
            time = 0
        storage.save_or_update_vk_user(chat_id=chat_id, notifications=time)
        await ans.answer('Минус 5 минут', keyboard=make_inline_keyboard_set_notifications(time))
        return

    elif '+' == message:
        time = user['notifications']
        time += 5
        storage.save_or_update_vk_user(chat_id=chat_id, notifications=time)
        await ans.answer('Плюс 5 минут', keyboard=make_inline_keyboard_set_notifications(time))

    elif 'Сохранить' in message:

        # Сохраняем статус в базу
        time = user['notifications']

        group = storage.get_vk_user(chat_id=chat_id)['group']

        if storage.get_vk_user(chat_id=chat_id)['course'] == "None":
            schedule = storage.get_schedule_prep(group=group)['schedule']
        else:
            schedule = storage.get_schedule(group=group)['schedule']
        if time > 0:
            reminders = calculating_reminder_times(schedule=schedule, time=int(time))
        else:
            reminders = []
        storage.save_or_update_vk_user(chat_id=chat_id, notifications=time, reminders=reminders)

        await ans.answer(f'{get_notifications_status(time)}', keyboard=make_keyboard_start_menu())


    elif 'Основное меню' in message and user.get('group'):
        await ans.answer('Основное меню', keyboard=make_keyboard_start_menu())
        add_statistics(action='Основное меню')

    elif '<==Назад' == message and user.get('group'):
        await ans.answer('Основное меню', keyboard=make_keyboard_start_menu())

    elif 'Далее' in message:
        await ans.answer('Далее', keyboard=make_keyboard_choose_group_vk_page_2())


    elif 'Список команд' == message and user.get('group'):
        await ans.answer('Список команд:\n'
                         'Авторы - список авторов \n'
                         'Регистрация- повторная регистрация\n'
                         'Карта - карта университета', keyboard=make_keyboard_commands())

        add_statistics(action='help')
        return

    elif 'Другое ⚡' == message and user.get('group'):
        await ans.answer('Другое', keyboard=make_keyboard_extra())

        add_statistics(action='help')
        return

    elif 'Поиск 🔎' == message and user.get('group'):

        await ans.answer('Выберите, что будем искать', keyboard=make_keyboard_search())



    else:
        await ans.answer('Такому ещё не научили 😇, знаю только эти команды:\n'
                         'Авторы - список авторов \n'
                         'Регистрация - повторная регистрация\n'
                         'Карта - карта университета')
        add_statistics(action='bullshit')


def main():
    '''Запуск бота'''
    bot.run_forever()


if __name__ == "__main__":
    main()
