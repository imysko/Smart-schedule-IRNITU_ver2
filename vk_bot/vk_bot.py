from actions import commands
from functions.creating_schedule import full_schedule_in_str, full_schedule_in_str_prep, get_one_day_schedule_in_str, \
    get_next_day_schedule_in_str, get_one_day_schedule_in_str_prep, get_next_day_schedule_in_str_prep
from functions.calculating_reminder_times import calculating_reminder_times
from functions.near_lesson import get_near_lesson, get_now_lesson
from functions.storage import MongodbService
from vkbottle_types import BaseStateGroup
from functions.find_week import find_week
from tools.keyboards import *
import os
import pytz
from datetime import datetime
from vkbottle.bot import Bot, Message

from tools import schedule_processing, statistics
from actions.registration import teacher_registration
from actions.search import prep_and_group_search, aud_search

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

map_image = "photo-198983266_457239216"


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


# ==================== ПОИСК ==================== #

class SuperStates(BaseStateGroup):
    SEARCH = 0
    PREP_REG = 1
    AUD_SEARCH = 2


@bot.on.message(state=SuperStates.PREP_REG)  # Стейт регистрации преподавателей
async def reg_prep_handler(ans: Message):
    """Стейт регистрации преподавателей"""
    await teacher_registration.reg_prep(bot=bot, ans=ans, storage=storage)


@bot.on.message(text="Группы и преподаватели")  # Вхождение в стейт поиска
async def start_search_handler(ans: Message):
    """Вхождение в стейт поиска"""
    await prep_and_group_search.start_search(bot=bot, ans=ans, state=SuperStates, storage=storage)


@bot.on.message(state=SuperStates.SEARCH)  # Стейт для работы поиска
async def search_handler(ans: Message):
    await prep_and_group_search.search(bot=bot, ans=ans, storage=storage)


@bot.on.message(text="Преподаватель")  # Вхождение в стейт регистрации преподавателей
async def start_prep_reg_handler(ans: Message):
    await teacher_registration.start_prep_reg(bot=bot, ans=ans, state=SuperStates, storage=storage)


@bot.on.message(text="Аудитории")  # Вхождение в стейт поиска аудитории
async def start_aud_search_handler(ans: Message):
    """Вхождение в стейт поиска аудитории"""
    await aud_search.start_search(bot=bot, ans=ans, state=SuperStates)


@bot.on.message(state=SuperStates.AUD_SEARCH)  # Стейт поиска по аудиториям
async def aud_search_handler(ans: Message):
    await aud_search.search(bot=bot, ans=ans, storage=storage)


# ==================== Обработка команд ==================== #


# Команда start
@bot.on.message(text=сontent_commands['text'])
async def start_message_handler(ans: Message):
    chat_id = ans.from_id
    await commands.start(ans=ans, chat_id=chat_id, storage=storage)
    statistics.add(action='start', storage=storage, tz=TZ_IRKUTSK)


# Команда Регистрация
@bot.on.message(text='Регистрация')
async def registration_handler(ans: Message):
    chat_id = ans.from_id
    await commands.registration(ans=ans, chat_id=chat_id, storage=storage)
    statistics.add(action='reg', storage=storage, tz=TZ_IRKUTSK)


# Команда Карта
@bot.on.message(text=content_map['text'])
async def show_map_handler(ans: Message):
    await commands.show_map(ans=ans, photo_vk_name=map_image)
    statistics.add(action='map', storage=storage, tz=TZ_IRKUTSK)


# Команда Авторы
@bot.on.message(text='Авторы')
async def authors_handler(ans: Message):
    await commands.authors(ans=ans)
    statistics.add(action='authors', storage=storage, tz=TZ_IRKUTSK)


@bot.on.message(text=content_types['text'])
async def scheduler(ans: Message):
    chat_id = ans.from_id
    data = ans.text
    user = storage.get_vk_user(chat_id=chat_id)

    if 'Расписание 🗓' == data and user.get('group'):
        await ans.answer('Выберите период\n', keyboard=make_keyboard_choose_schedule())
        statistics.add(action='Расписание', storage=storage, tz=TZ_IRKUTSK)

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
            statistics.add(action=data, storage=storage, tz=TZ_IRKUTSK)
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

        statistics.add(action=data, storage=storage, tz=TZ_IRKUTSK)



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
            statistics.add(action='Расписание на сегодня', storage=storage, tz=TZ_IRKUTSK)
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
        statistics.add(action='Расписание на сегодня', storage=storage, tz=TZ_IRKUTSK)

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
            statistics.add(action='Расписание на завтра', storage=storage, tz=TZ_IRKUTSK)
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
        statistics.add(action='Расписание на завтра', storage=storage, tz=TZ_IRKUTSK)

    elif 'Ближайшая пара ⏱' in data and user.get('group'):
        await ans.answer('Ближайшая пара', keyboard=make_keyboard_nearlesson())
        statistics.add(action='Ближайшая пара', storage=storage, tz=TZ_IRKUTSK)
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
            statistics.add(action='Текущая', storage=storage, tz=TZ_IRKUTSK)
            return
        schedule = schedule['schedule']
        week = find_week()

        now_lessons = get_now_lesson(schedule=schedule, week=week)

        # если пар нет
        if not now_lessons:
            await ans.answer('Сейчас пары нет, можете отдохнуть)', keyboard=make_keyboard_start_menu())
            statistics.add(action='Текущая', storage=storage, tz=TZ_IRKUTSK)
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

        statistics.add(action='Текущая', storage=storage, tz=TZ_IRKUTSK)

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
            statistics.add(action='Следующая', storage=storage, tz=TZ_IRKUTSK)
            return
        schedule = schedule['schedule']
        week = find_week()

        near_lessons = get_near_lesson(schedule=schedule, week=week)

        # если пар нет
        if not near_lessons:
            await ans.answer('Сегодня больше пар нет 😎', keyboard=make_keyboard_start_menu())
            statistics.add(action='Следующая', storage=storage, tz=TZ_IRKUTSK)
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

        statistics.add(action='Следующая', storage=storage, tz=TZ_IRKUTSK)


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

        statistics.add(action='Напоминание', storage=storage, tz=TZ_IRKUTSK)

    elif 'Настройки' in message and user.get('group'):
        time = user['notifications']
        await ans.answer('Настройка напоминаний ⚙\n\n'
                         'Укажите за сколько минут до начала пары должно приходить сообщение',
                         keyboard=make_inline_keyboard_set_notifications(time))
        statistics.add(action='Настройки', storage=storage, tz=TZ_IRKUTSK)

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
        statistics.add(action='Основное меню', storage=storage, tz=TZ_IRKUTSK)

    elif '<==Назад' == message and user.get('group'):
        await ans.answer('Основное меню', keyboard=make_keyboard_start_menu())

    elif 'Далее' in message:
        await ans.answer('Далее', keyboard=make_keyboard_choose_group_vk_page_2())


    elif 'Список команд' == message and user.get('group'):
        await ans.answer('Список команд:\n'
                         'Авторы - список авторов \n'
                         'Регистрация- повторная регистрация\n'
                         'Карта - карта университета', keyboard=make_keyboard_commands())

        statistics.add(action='help', storage=storage, tz=TZ_IRKUTSK)
        return

    elif 'Другое ⚡' == message and user.get('group'):
        await ans.answer('Другое', keyboard=make_keyboard_extra())
        statistics.add(action='Другое', storage=storage, tz=TZ_IRKUTSK)
        return

    elif 'Поиск 🔎' == message and user.get('group'):

        await ans.answer('Выберите, что будем искать', keyboard=make_keyboard_search())



    else:
        await ans.answer('Такому ещё не научили 😇, знаю только эти команды:\n'
                         'Авторы - список авторов \n'
                         'Регистрация - повторная регистрация\n'
                         'Карта - карта университета')
        statistics.add(action='bullshit', storage=storage, tz=TZ_IRKUTSK)


def main():
    """Запуск бота"""
    bot.run_forever()


if __name__ == "__main__":
    main()
