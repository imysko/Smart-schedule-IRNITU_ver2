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
longpoll= VkLongPoll(authorize)
MAX_CALLBACK_RANGE = 41
storage = MongodbService().get_instance()
bot = Bot(f"{os.environ.get('VK')}", debug="DEBUG") # TOKEN
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


def make_keyboard_institutes(institutes =[]):
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
    '''Создаёт клавиатуру для выбора группы'''

    keyboard = {
        "one_time": False
    }
    global list_keyboard_main_2
    global all_groups
    overflow = 0
    list_keyboard_main_2 = []
    list_keyboard_main = []
    list_keyboard = []
    for group in groups:
        if choice in group['institute']:
            name = group['name']
            all_groups.append(name)
            overflow+=1
            if overflow == 27:
                list_keyboard_main.append(list_keyboard)
                list_keyboard = []
                list_keyboard.append(parametres_for_buttons_start_menu_vk('Далее', 'primary'))
                list_keyboard_main.append(list_keyboard)
            else:
                if overflow < 28 :
                    if len(list_keyboard) == 3:
                        list_keyboard_main.append(list_keyboard)
                        list_keyboard = []
                        list_keyboard.append(parametres_for_buttons_start_menu_vk(f'{name}', 'primary'))
                    else:
                        list_keyboard.append(parametres_for_buttons_start_menu_vk(f'{name}', 'primary'))
                else:
                    list_keyboard = []
                    list_keyboard.append(parametres_for_buttons_start_menu_vk(f'{name}', 'primary'))
                    list_keyboard_main_2.append(list_keyboard)
    if overflow < 28:
        list_keyboard_main.append(list_keyboard)
    else:
        list_keyboard_main_2.append(list_keyboard)
    keyboard['buttons'] = list_keyboard_main
    return keyboard

def make_keyboard_choose_group_vk_page_2(groups=[]):
    '''Создаёт клавиатуру для групп после переполнения первой'''
    keyboard = {
        "one_time": False
    }
    list_keyboard_main = []
    list_keyboard = []
    for group in groups:
        if len(list_keyboard) == 3:
            list_keyboard_main.append(list_keyboard)
            list_keyboard = []
        else:
            list_keyboard.append(*group)
    list_keyboard_main.append(list_keyboard)
    list_keyboard_main.append([parametres_for_buttons_start_menu_vk('Назад', 'primary')])
    keyboard['buttons'] = list_keyboard_main
    return keyboard

def sep_space(name):
    '''Обрезает длину института, если тот больше 40 символов'''
    dlina = abs(len(name) - MAX_CALLBACK_RANGE)
    name = name[:len(name) - dlina-5]
    return name

def name_institutes(institutes = []):
    '''Храним список всех институтов'''
    list_institutes = []
    for i in institutes:
        name = i['name']
        list_institutes.append(name)
    return list_institutes

def name_groups(groups = []):
    '''Храним список всех групп'''
    list_groups = []
    for i in groups:
        name = i['name']
        list_groups.append(name)
    return list_groups

def listening():
    '''Ждёт сообщение'''
    for event in longpoll.listen():
        print(dir(event))
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                id = event.user_id
                message = event.text
                return message

@bot.on.message(text='Хай')
async def wrapper(ans: Message):
    '''Начало регистрации'''
    await ans('Привет\n')
    await ans('Для начала пройдите небольшую регистрацию😉\n')
    await ans('Выберите институт.', keyboard=make_keyboard_institutes(storage.get_institutes()))
    x = listening()
    while True:
        inst = listening()
        institutes = name_institutes(storage.get_institutes())
        if inst in institutes:
            await ans('Выберите курс.', keyboard=make_keyboard_choose_course_vk(storage.get_courses(inst)))
            break
        else:
            await ans('Я тебя не понял, выбери институт и не еби мозгу\n')

    while True:
        group = listening()
        groups = name_groups(storage.get_groups())
        if group in groups:
            await ans('Выберите курс.', keyboard=make_keyboard_choose_course_vk(storage.get_courses(inst)))
            break
        else:
            await ans('Я тебя не понял, выбери институт и не еби мозгу\n')

def main():
    '''Запуск бота'''
    bot.run_polling()

if __name__ == "__main__":
    main()

