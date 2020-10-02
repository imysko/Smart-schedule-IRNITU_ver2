from vk_api import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from vkbottle.bot import Bot, Message
from functions.storage import MongodbService
from vkbottle.keyboard import Keyboard, Text
from vkbottle.api.keyboard import keyboard_gen
from vkbottle.ext import Middleware
import vk
import json
import typing
from aiohttp import web
import os

token = os.environ.get('VK')
authorize = vk_api.VkApi(token=token)
longpoll = VkLongPoll(authorize)
MAX_CALLBACK_RANGE = 41
storage = MongodbService().get_instance()
bot = Bot(f"{os.environ.get('VK')}", debug="DEBUG")  # TOKEN
database: typing.Dict[int, str] = {}  # Наш прототип базы данных


def parametres_for_buttons_start_menu_vk(text, color):
    '''Возвращает параметры кнопок'''
    return {
        "action": {
            "type": "text",
            "payload": "{\"button\": \"" + "1" + "\"}",
            "label": f"{text}"
        },
        "color": f"{color}"
    }


def make_keyboard_start_menu():
    """Создаём основные кнопки"""
    keyboard = Keyboard(one_time=False)
    keyboard.add_row()
    keyboard.add_button(Text(label="Рас"), color="primary")
    keyboard.add_button(Text(label="Ближайшая пара"), color="primary")
    keyboard.add_row()
    keyboard.add_button(Text(label="Напоминание"), color="default")
    return keyboard


def make_keyboard_institutes(institutes=[]):
    """Кнопки выбора института"""
    keyboard = {
        "one_time": False
    }
    list_keyboard_main = []
    for institute in institutes:
        if len(institute['name']) >= MAX_CALLBACK_RANGE:
            name = sep_space(institute['name'])
        else:
            name = institute['name']
        list_keyboard = []
        list_keyboard.append(parametres_for_buttons_start_menu_vk(f'{name}', 'primary'))
        list_keyboard_main.append(list_keyboard)
    keyboard['buttons'] = list_keyboard_main
    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard


def make_keyboard_choose_course_vk(courses):
    '''Создаёт клавиатуру для выбора курса'''
    keyboard = {
        "one_time": False
    }
    list_keyboard_main = []
    for course in courses:
        name = course['name']
        list_keyboard = []
        list_keyboard.append(parametres_for_buttons_start_menu_vk(f'{name}', 'primary'))
        list_keyboard_main.append(list_keyboard)
    keyboard['buttons'] = list_keyboard_main
    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard


def make_keyboard_choose_group_vk(groups=[]):
    """Кнопки выбора института"""
    keyboard = {
        "one_time": False
    }
    list_keyboard_main = []
    for group in groups:
        list_keyboard = []
        list_keyboard.append(parametres_for_buttons_start_menu_vk(f'{group}', 'primary'))
        list_keyboard_main.append(list_keyboard)
    keyboard['buttons'] = list_keyboard_main
    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard


def sep_space(name):
    '''Обрезает длину института, если тот больше 40 символов'''
    dlina = abs(len(name) - MAX_CALLBACK_RANGE)
    name = name[:len(name) - dlina - 5]
    return name


def name_institutes(institutes=[]):
    '''Храним список всех институтов'''
    list_institutes = []
    for i in institutes:
        name = i['name']
        list_institutes.append(name)
    return list_institutes


def name_courses(courses=[]):
    '''Храним список всех институтов'''
    list_courses = []
    for i in courses:
        name = i['name']
        list_courses.append(name)
    return list_courses


def name_groups(groups=[]):
    '''Храним список всех групп'''
    list_groups = []
    for i in groups:
        name = i['name']
        list_groups.append(name)
    return list_groups


def listening():
    '''Ждёт сообщение'''
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                id = event.user_id
                message = event.text
                return message


@bot.on.message(text='/start')
async def start(ans: Message):
    '''Начало регистрации'''
    chat_id = ans.from_id
    # Проверяем есть пользователь в базе данных
    if storage.get_user(chat_id):
        storage.delete_user_or_userdata(chat_id)  # Удаляем пользвателя из базы данных
    await ans('Привет\n')
    await ans('Для начала пройдите небольшую регистрацию😉\n')
    await ans('Выберите институт.', keyboard=make_keyboard_institutes(storage.get_institutes()))


@bot.on.message()
async def wrapper(ans: Message):
    chat_id = ans.from_id
    message = ans.text
    user = storage.get_user(chat_id)
    #Если пользователя нет в базе данных
    if not user:
        institutes = name_institutes(storage.get_institutes())
        #Смотрим выбра ли пользователь институт
        if message in institutes:
            #Если да, то записываем в бд
            storage.save_or_update_user(chat_id=chat_id, institute=message)
            await ans('Найс\n')
            await ans('Выберите курс.', keyboard=make_keyboard_choose_course_vk(storage.get_courses(message)))
        else:
            await ans('Я вас не понимаю\n')
        return
    #Регистрация после выбора института
    elif not 'course' in user.keys():
        institute = user['institute']
        course = storage.get_courses(institute)
        #Если нажал кнопку курса
        if message in name_courses(course):
            #Записываем в базу данных выбранный курс
            storage.save_or_update_user(chat_id=chat_id, course=message)
            groups = storage.get_groups(institute=institute, course=message)
            groups = name_groups(groups)
            await ans('Выберите группу.', keyboard=make_keyboard_choose_group_vk(groups))
            await ans('Найс2\n')
        else:
            await ans('Я вас не понимаю\n')
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
            storage.save_or_update_user(chat_id=chat_id, group=message )
            await ans('Конграт!\n')
        else:
            await ans('Я вас не понимаю\n')
        return




def main():
    '''Запуск бота'''
    bot.run_polling()


if __name__ == "__main__":
    main()
