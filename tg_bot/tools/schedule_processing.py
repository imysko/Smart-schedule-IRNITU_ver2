

def sending_schedule(bot, message, schedule_str: str):
    """Отправка расписания пользователю"""
    chat_id = message.chat.id
    for schedule in schedule_str:
        bot.send_message(chat_id=chat_id, text=f'{schedule}')


def sending_schedule_is_not_available(bot, message):
    chat_id = message.chat.id
    bot.send_message(chat_id=chat_id, text='Расписание временно недоступно\n'
                                           'Попробуйте позже⏱')

def sending_schedule_serach(bot, message, chat_id, schedule_str: str):
    """Отправка расписания пользователю"""
    for schedule in schedule_str:
        bot.send_message(chat_id=chat_id, text=f'{schedule}')


def sending_schedule_is_not_available_search(bot, message, chat_id):
    bot.send_message(chat_id=chat_id, text='Расписание временно недоступно\n'
                                           'Попробуйте позже⏱')