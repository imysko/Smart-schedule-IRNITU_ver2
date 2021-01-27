from actions import commands
from actions.main_menu import reminders
from functions.creating_schedule import full_schedule_in_str, full_schedule_in_str_prep, get_one_day_schedule_in_str, \
    get_next_day_schedule_in_str, get_one_day_schedule_in_str_prep, get_next_day_schedule_in_str_prep

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
from actions.registration import teacher_registration, student_registration
from actions.search import prep_and_group_search, aud_search

TOKEN = os.environ.get('VK')

# Обьявление некоторых глбальных переменных


storage = MongodbService().get_instance()
bot = Bot(TOKEN)  # TOKEN

content_types = {
    'text': ['Расписание 🗓', 'Ближайшая пара ⏱', 'Расписание на сегодня 🍏', 'На текущую неделю',
             'На следующую неделю',
             'Расписание на завтра 🍎', 'Следующая', 'Текущая']}

content_commands = {'text': ['Начать', 'начать', 'Начало', 'start']}

content_reminders = {'text': ['Напоминание 📣', 'Настройки ⚙', '-', '+', 'Сохранить']}

content_map = {'text': ['map', 'Карта', 'карта', 'Map', 'Схема', 'схема']}

TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk')

map_image = "photo-198983266_457239216"


# ==================== Создание основных клавиатур и кнопок ==================== #


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
@bot.on.message(text=content_commands['text'])
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


@bot.on.message(text=content_reminders['text'])
async def reminders_handler(ans: Message):
    """Настройка напоминаний"""
    await reminders.reminder_settings(ans=ans, storage=storage, tz=TZ_IRKUTSK)


@bot.on.message()
async def wrapper(ans: Message):
    """Регистрация пользователя"""
    await student_registration.start_student_reg(ans=ans, storage=storage, tz=TZ_IRKUTSK)


def main():
    """Запуск бота"""
    bot.run_forever()


if __name__ == "__main__":
    main()
