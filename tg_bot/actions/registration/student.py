import json

from telebot import TeleBot
from db import data_conversion, postgre_storage
from db.mongo_storage import MongodbServiceTG
from tools.tg_tools import inline_keyboards, reply_keyboards
from tools.messages import registration_messages
from tools.logger import logger


def start_student_registration(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.message.chat.id
    message_id = message.message.message_id
    data = message.data

    institutes = data_conversion.convert_institutes(
        postgre_storage.get_institutes()
    )

    bot.edit_message_text(
        message_id=message_id,
        chat_id=chat_id,
        text=registration_messages['select_institute'],
        reply_markup=inline_keyboards.keyboard_institutes(institutes)
    )

    logger.info(f'Inline button data: {data}')


def select_course_student_registration(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.message.chat.id
    message_id = message.message.message_id
    data = message.data

    institute_id = storage.get_user(chat_id)['institute']

    courses = postgre_storage.get_courses_by_institute(institute_id)

    bot.edit_message_text(
        message_id=message_id,
        chat_id=chat_id,
        text=registration_messages['select_course'],
        reply_markup=inline_keyboards.keyboard_courses(courses)
    )

    logger.info(f'Inline button data: {data}')


def select_group_student_registration(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.message.chat.id
    message_id = message.message.message_id
    data = message.data

    user = storage.get_user(chat_id)

    institute_id = user['institute']
    course = json.loads(data)['course']

    groups = data_conversion.convert_groups(
        postgre_storage.get_groups_by_institute_and_course(
            institute_id=institute_id,
            course=course
        )
    )

    bot.edit_message_text(
        message_id=message_id,
        chat_id=chat_id,
        text=registration_messages['select_group'],
        reply_markup=inline_keyboards.keyboard_groups(groups)
    )

    logger.info(f'Inline button data: {data}')


def finish_student_registration(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.message.chat.id
    message_id = message.message.message_id
    data = message.data

    bot.delete_message(chat_id, message_id)
    bot.send_message(
        chat_id=chat_id,
        text=registration_messages['successful_registration'],
        reply_markup=reply_keyboards.keyboard_start_menu()
    )

    logger.info(f'Inline button data: {data}')
