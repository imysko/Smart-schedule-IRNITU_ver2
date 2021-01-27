from functions.storage import MongodbService
from vkbottle_types import BaseStateGroup

import os
import pytz
from vkbottle.bot import Bot, Message

from tools import statistics
from actions.registration import teacher_registration, student_registration
from actions.search import prep_and_group_search, aud_search
from actions import commands
from actions.main_menu import reminders, main_menu, schedule

TOKEN = os.environ.get('VK')

# Обьявление некоторых глбальных переменных


storage = MongodbService().get_instance()
bot = Bot(TOKEN)  # TOKEN

content_schedule = {
    'text': ['Расписание 🗓', 'Ближайшая пара ⏱', 'Расписание на сегодня 🍏', 'На текущую неделю',
             'На следующую неделю',
             'Расписание на завтра 🍎', 'Следующая', 'Текущая']}

content_commands = {'text': ['Начать', 'начать', 'Начало', 'start']}

content_main_menu_buttons = {'text': ['Основное меню', '<==Назад', 'Список команд', 'Другое ⚡', 'Поиск 🔎']}

content_reminders = {'text': ['Напоминание 📣', 'Настройки ⚙', '-', '+', 'Сохранить']}

content_map = {'text': ['map', 'Карта', 'карта', 'Map', 'Схема', 'схема']}

TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk')

map_image = "photo-198983266_457239216"


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


@bot.on.message(text=content_schedule['text'])
async def schedule_handler(ans: Message):
    """Получение расписания"""
    await schedule.get_schedule(ans=ans, storage=storage, tz=TZ_IRKUTSK)


@bot.on.message(text=content_main_menu_buttons['text'])
async def main_menu_buttons_handler(ans: Message):
    """Основные кнопки главног меню"""
    await main_menu.processing_main_buttons(ans=ans, storage=storage, tz=TZ_IRKUTSK)


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
