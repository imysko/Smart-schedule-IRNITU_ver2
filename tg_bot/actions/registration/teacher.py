import json

from thefuzz import process
from telebot import TeleBot

from tools.messages import registration_messages
from db.mongo_storage import MongodbServiceTG
from db import postgre_storage
from tools.tg_tools import reply_keyboards, inline_keyboards


def find_teacher(fullname: str, teachers_list: list) -> list:
    teachers_names = [user['fullname'] for user in teachers_list]
    search_result = process.extract(fullname, teachers_names, limit=3)
    good_results = []
    for teacher in search_result:
        if teacher[1] > 70:
            good_results.append(teacher[0])
    print(good_results)
    final_result = []
    for teacher in good_results:
        final_result.append(list(filter(lambda user: user['fullname'] == teacher, teachers_list))[0])
    return final_result


def start_teacher_registration(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.message.chat.id
    message_id = message.message.message_id

    msg = bot.send_message(
        chat_id=chat_id,
        text=registration_messages['enter_full_name']
    )

    bot.register_next_step_handler(msg, finish_teacher_registration, bot, storage)
    bot.delete_message(
        message_id=message_id,
        chat_id=chat_id
    )


def finish_teacher_registration(message, bot: TeleBot, storage: MongodbServiceTG, last_msg=None):
    chat_id = message.chat.id
    text = message.text

    if last_msg:
        message_id = last_msg.message_id
        bot.delete_message(
            message_id=message_id,
            chat_id=chat_id
        )

    teachers_list = postgre_storage.get_teachers()

    teacher = list(filter(lambda user: user['fullname'] == text, teachers_list))
    if len(teacher) != 0:
        storage.save_or_update_user(
            chat_id=chat_id,
            institute='teacher',
            group=teacher
        )
        bot.send_message(
            chat_id=chat_id,
            text=registration_messages['successful_registration'],
            reply_markup=reply_keyboards.keyboard_start_menu()
        )
    else:
        teachers = find_teacher(text, teachers_list)
        if len(teachers) == 0:
            bot.send_message(
                chat_id=chat_id,
                text=registration_messages['wrong_teacher_name'],
                reply_markup=inline_keyboards.keyboard_user_role()
            )
        else:
            bot.send_message(
                chat_id=chat_id,
                text=registration_messages['probably_you_mean'],
                reply_markup=inline_keyboards.keyboard_with_possible_teachers(teachers)
            )


def finish_teacher_registration_by_button(message, bot: TeleBot, storage: MongodbServiceTG):
    chat_id = message.message.chat.id
    data = json.loads(message.data)

    if data['register_teacher_id'] == 'cancel':
        bot.send_message(
            chat_id=chat_id,
            text=registration_messages['new_registration'],
            reply_markup=inline_keyboards.keyboard_user_role()
        )
        return

    teacher_id = data['register_teacher_id']
    teachers_list = postgre_storage.get_teachers()

    teacher = list(filter(lambda user: user['teacher_id'] == teacher_id, teachers_list))[0]
    storage.save_or_update_user(
        chat_id=chat_id,
        institute='teacher',
        group=teacher['teacher_id']
    )
    bot.send_message(
        chat_id=chat_id,
        text=registration_messages['successful_registration'],
        reply_markup=reply_keyboards.keyboard_start_menu()
    )
