from telebot import TeleBot


def start_student_registration(bot: TeleBot, message, storage):
    chat_id = message.chat.id

    bot.send_message(
        chat_id=chat_id,
        text='Регетстрация начата!'
    )
