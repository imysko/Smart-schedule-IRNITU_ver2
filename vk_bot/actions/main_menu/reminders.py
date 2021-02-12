from vkbottle.bot import Message

from API.functions_api import calculating_reminder_times, get_notifications_status, APIError
from tools import keyboards, statistics, schedule_processing


async def reminder_settings(ans: Message, storage, tz):
    chat_id = ans.from_id
    message = ans.text
    user = storage.get_vk_user(chat_id)

    time = user['notifications']
    if not time:
        time = 0

    # Проверяем статус напоминания
    notifications_status = get_notifications_status(time)
    if isinstance(notifications_status, APIError):
        await schedule_processing.sending_service_is_not_available(ans=ans)
        return

    if message == 'Напоминание 📣' and user.get('group'):
        await ans.answer(f'{notifications_status}', keyboard=keyboards.make_inline_keyboard_notifications())
        statistics.add(action='Напоминание', storage=storage, tz=tz)

    elif message == 'Настройки ⚙' and user.get('group'):
        await ans.answer('Настройка напоминаний ⚙\n\n'
                         'Укажите за сколько минут до начала пары должно приходить сообщение',
                         keyboard=keyboards.make_inline_keyboard_set_notifications(time))
        statistics.add(action='Настройки', storage=storage, tz=tz)

    elif '-' == message:
        if time == 0:
            await ans.answer('Хочешь уйти в минус?', keyboard=keyboards.make_inline_keyboard_set_notifications(time))
            return
        time -= 5
        # Отнимаем и проверяем на положительность
        if time <= 0:
            time = 0
        storage.save_or_update_vk_user(chat_id=chat_id, notifications=time)
        await ans.answer('Минус 5 минут', keyboard=keyboards.make_inline_keyboard_set_notifications(time))
        return

    elif '+' == message:
        time += 5
        storage.save_or_update_vk_user(chat_id=chat_id, notifications=time)
        await ans.answer('Плюс 5 минут', keyboard=keyboards.make_inline_keyboard_set_notifications(time))

    elif message == 'Сохранить':
        # Сохраняем статус в базу
        group = storage.get_vk_user(chat_id=chat_id)['group']

        if storage.get_vk_user(chat_id=chat_id)['course'] == "None":
            schedule = storage.get_schedule_prep(group=group)['schedule']
        else:
            schedule = storage.get_schedule(group=group)['schedule']
        if time > 0:
            reminders = calculating_reminder_times(schedule=schedule, time=int(time))
        else:
            reminders = []
        storage.save_or_update_vk_user(chat_id=chat_id, notifications=time, reminders=reminders)

        await ans.answer(f'{get_notifications_status(time)}', keyboard=keyboards.make_keyboard_start_menu())
