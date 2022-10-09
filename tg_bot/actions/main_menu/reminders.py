import json

from tools.schedule_tools.notifications import *
from tools.tg_tools import keyboards, schedule_processing
from tools.logger import logger
from tools import statistics


def reminder_info(bot, message, storage, tz):
    chat_id = message.chat.id
    user = storage.get_user(chat_id=chat_id)

    time = user['notifications']
    if not time:
        time = 0

    # Проверяем статус напоминания
    notifications_status = get_notifications_status(time)
    if isinstance(notifications_status, None):
        schedule_processing.sending_service_is_not_available(bot, chat_id)
        return

    if user:
        bot.send_message(chat_id=chat_id, text=notifications_status,
                         reply_markup=keyboards.make_inline_keyboard_notifications(time))

        statistics.add(action='Напоминания', storage=storage, tz=tz)


def reminder_settings(bot, message, storage, tz):
    chat_id = message.message.chat.id
    message_id = message.message.message_id
    data = message.data

    if 'notification_btn' in data:
        data = json.loads(data)
        if data['notification_btn'] == 'close':
            try:
                bot.delete_message(message_id=message_id, chat_id=chat_id)
                return
            except Exception as e:
                logger.exception(e)
                return
        time = data['notification_btn']

        # Проверяем статус напоминания
        notifications_status = get_notifications_status(time)
        if isinstance(notifications_status, None):
            schedule_processing.sending_service_is_not_available(bot, chat_id)
            return

        try:
            bot.edit_message_text(message_id=message_id, chat_id=chat_id,
                                  text='Настройка напоминаний ⚙\n\n'
                                       'Укажите за сколько минут до начала пары должно приходить сообщение',
                                  reply_markup=keyboards.make_inline_keyboard_set_notifications(time))
        except Exception as e:
            logger.exception(e)
            return

    elif 'del_notifications' in data:
        data = json.loads(data)
        time = data['del_notifications']
        if time == 0:
            return
        time -= 5

        if time < 0:
            time = 0

        # Проверяем статус напоминания
        notifications_status = get_notifications_status(time)
        if isinstance(notifications_status, None):
            schedule_processing.sending_service_is_not_available(bot, chat_id)
            return

        try:
            bot.edit_message_reply_markup(message_id=message_id, chat_id=chat_id,
                                          reply_markup=keyboards.make_inline_keyboard_set_notifications(time))
        except Exception as e:
            logger.exception(e)
            return

    elif 'add_notifications' in data:
        data = json.loads(data)
        time = data['add_notifications']
        time += 5

        # Проверяем статус напоминания
        notifications_status = get_notifications_status(time)
        if isinstance(notifications_status, None):
            schedule_processing.sending_service_is_not_available(bot, chat_id)
            return

        try:
            bot.edit_message_reply_markup(message_id=message_id, chat_id=chat_id,
                                          reply_markup=keyboards.make_inline_keyboard_set_notifications(time))
        except Exception as e:
            logger.exception(e)
            return

    elif 'save_notifications' in data:
        data = json.loads(data)
        time = data['save_notifications']

        # Проверяем статус напоминания
        notifications_status = get_notifications_status(time)
        if isinstance(notifications_status, None):
            schedule_processing.sending_service_is_not_available(bot, chat_id)
            return

        group = storage.get_user(chat_id=chat_id)['group']

        if storage.get_user(chat_id=chat_id)['course'] == 'None':
            schedule = storage.get_schedule_prep(group=group)['schedule']
        else:
            schedule = storage.get_schedule(group=group)['schedule']

        if time > 0:
            reminders = calculating_reminder_times(schedule=schedule, time=int(time))
        else:
            reminders = []
        storage.save_or_update_user(chat_id=chat_id, notifications=time, reminders=reminders)

        try:
            bot.edit_message_text(message_id=message_id, chat_id=chat_id, text=get_notifications_status(time),
                                  reply_markup=keyboards.make_inline_keyboard_notifications(time))
        except Exception as e:
            logger.exception(e)
            return

        statistics.add(action='save_notifications', storage=storage, tz=tz)
