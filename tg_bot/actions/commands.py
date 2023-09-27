from telebot import TeleBot

from db.mongo_storage import MongodbServiceTG
from tools.messages import registration_messages, other_messages
from tools.tg_tools import inline_keyboards, reply_keyboards


def start(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.chat.id

    user = storage.get_user(chat_id)
    if user:
        bot.send_message(
            chat_id=chat_id,
            text=registration_messages['successful_registration'],
            reply_markup=reply_keyboards.keyboard_start_menu()
        )
    else:
        # storage.delete_user_or_userdata(chat_id)
        bot.send_message(
            chat_id=chat_id,
            text=registration_messages['new_registration'],
            reply_markup=inline_keyboards.keyboard_user_role()
        )


def registration(bot: TeleBot, message, storage: MongodbServiceTG, edit: bool = False):
    chat_id = message.chat.id
    message_id = message.message_id

    # storage.delete_user_or_userdata(chat_id)
    if not edit:
        bot.send_message(
            chat_id=chat_id,
            text=registration_messages['repeat_registration'],
            reply_markup=inline_keyboards.keyboard_user_role()
        )
    else:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=registration_messages['repeat_registration'],
            reply_markup=inline_keyboards.keyboard_user_role()
        )


def help(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.chat.id
    bot.send_message(
        chat_id=chat_id,
        text=other_messages['help_message']
    )

def sqlite(bot: TeleBot, message):
    with open("sqlite.db.zip", 'rb') as f:
        bot.send_document(chat_id=message.chat.id, document=f)


def about(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.chat.id

    bot.send_message(
        chat_id=chat_id,
        parse_mode='HTML',
        text=other_messages['about_message']
    )


def show_map(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.chat.id
    bot.send_message(
        chat_id,
        text=other_messages['map_message']
    )


def authors(bot: TeleBot, message, storage: MongodbServiceTG):
    chat_id = message.chat.id

    bot.send_message(
        chat_id=chat_id,
        parse_mode='HTML',
        text=other_messages['author_message']
    )
