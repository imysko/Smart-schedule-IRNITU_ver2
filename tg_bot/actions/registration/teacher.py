from telebot import TeleBot

from tools.messages import registration_messages
from db.mongo_storage import MongodbServiceTG
from db import postgre_storage
from tools.tg_tools import reply_keyboards, inline_keyboards


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
    message = message.text

    if last_msg:
        message_id = last_msg.message_id
        bot.delete_message(
            message_id=message_id,
            chat_id=chat_id
        )

    teachers_list = postgre_storage.get_teachers()

    if message in teachers_list:
        storage.save_or_update_user(
            chat_id=chat_id,
            institute='teacher',
            course='None',
            group=message
        )
        bot.send_message(
            chat_id=chat_id,
            text=registration_messages['successful_registration'],
            reply_markup=reply_keyboards.keyboard_start_menu()
        )
    else:
        msg = bot.send_message(
            chat_id=chat_id,
            text=registration_messages['wrong_teacher_name']
        )
        bot.register_next_step_handler(msg, finish_teacher_registration, bot, storage)

