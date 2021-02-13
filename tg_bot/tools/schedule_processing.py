from tools import keyboards


def sending_schedule(bot, chat_id, schedule_str: str):
    """Отправка расписания пользователю"""
    for schedule in schedule_str:
        bot.send_message(chat_id=chat_id, text=f'{schedule}')


def sending_schedule_is_not_available(bot, chat_id):
    bot.send_message(chat_id=chat_id, text='Расписание временно недоступно🚫😣\n'
                                           'Попробуйте позже⏱')


def sending_service_is_not_available(bot, chat_id):
    bot.send_message(chat_id=chat_id, text='Сервис временно недоступен🚫😣\n'
                                           'Попробуйте позже⏱',
                     keyboard=keyboards.make_keyboard_start_menu())
