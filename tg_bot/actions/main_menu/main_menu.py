from tools.tg_tools import reply_keyboards


def processing_main_buttons(bot, message, storage):
    chat_id = message.chat.id
    data = message.text
    user = storage.get_user(chat_id=chat_id)

    if 'Основное меню' in data and user:
        bot.send_message(chat_id, text='Основное меню', reply_markup=reply_keyboards.keyboard_start_menu())

    elif 'Другое ⚡' in data and user:
        bot.send_message(chat_id, text='Другое', reply_markup=reply_keyboards.keyboard_extra())
