import pytz
import locale
import vk_api
import os
from datetime import datetime, timedelta
from storage import MongodbService
from vkbottle.bot import Bot, Message

import platform

TOKEN = os.environ.get('VK')
TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk')
locale_name = ('ru_RU.UTF-8' if platform.system() == 'Linux' else 'ru_RU')
locale.setlocale(locale.LC_TIME, locale_name)

bot = Bot(f"{os.environ.get('VK')}", debug="DEBUG")

authorize = vk_api.VkApi(token=TOKEN)

storage = MongodbService().get_instance()


def find_week():
    """определение текущей недели"""
    now = datetime.now()
    sep = datetime(now.year if now.month >= 9 else now.year - 1, 9, 1)
    d1 = sep - timedelta(days=sep.weekday())
    d2 = now - timedelta(days=now.weekday())

    parity = ((d2 - d1).days // 7) % 2
    return 'odd' if parity else 'even'


def sending_notifications(users: list):
    for user in users:
        print(user)
        chat_id = user['chat_id']
        week = user['week']
        day_now = user['day']
        time = user['time']
        group = user['group']
        notifications = user['notifications']

        schedule = storage.get_schedule(group=group)['schedule']

        lessons = None
        for day in schedule:
            # находим нужный день
            if day['day'] == day_now:
                lessons = day['lessons']
                break
        # если не нашлось переходем к след user
        if not lessons:
            continue
        lessons_for_reminders = ''

        for lesson in lessons:
            print(lesson)
            lesson_time = lesson['time']
            print(lesson_time)
            print(time)
            # находим нужные пары (в нужное время)
            if time in lesson_time and (lesson['week'] == week or lesson['week'] == 'all'):
                name = lesson['name']
                # пропускаем свободные дни
                if name == 'свободно':
                    continue
                # формируем сообщение
                lessons_for_reminders += '--------------------------------------\n'
                aud = lesson['aud']
                if aud:
                    aud = f'Аудитория: {aud}\n'
                time = lesson['time']
                info = lesson['info']
                prep = lesson['prep']

                lessons_for_reminders += f'Начало в {time}\n' \
                                         f'{aud}' \
                                         f'{name}\n' \
                                         f'{info} {prep}\n'
                lessons_for_reminders += '--------------------------------------\n'
        # если пары не нашлись переходим к след user
        if not lessons_for_reminders:
            continue
        # отправляем сообщение пользователю
        text = f'Через {notifications} минут пара\n', f'{lessons_for_reminders}'
        authorize.method('messages.send', {'user_id': chat_id, 'message': text, 'random_id': 0})


def search_for_reminders():
    print('reminders_vk is started')
    minutes_old = None
    while True:
        # определяем время сейчас
        time_now = datetime.now(TZ_IRKUTSK)
        day_now = datetime.now(TZ_IRKUTSK).strftime('%A').lower()
        hours_now = int(time_now.strftime('%H'))
        minutes_now = int(time_now.strftime('%M'))
        # отправлять сообщения нужно не раньше чем каждые 5 минут
        # if minutes_now % 2 == 0 and minutes_old != minutes_now:
        if minutes_old != minutes_now:  # это для отладки!!!!!!!!!!!!!!!!!!!!!!!!!!!
            minutes_old = minutes_now  # нужно для того чтобы выполнить тело только один раз
            users = []

            # получаем пользователей у которых включены напоминания
            reminders = storage.get_users_with_reminders_vk()

            for reminder in reminders:
                week = find_week()

                if not 'reminders' in reminder.keys():
                    continue

                # если у пользователя пустой reminders то None
                user_days = reminder['reminders'].get(week)
                if not user_days:
                    continue
                # если у пользователя нет ткущего дня, то None
                user_day_time = user_days.get(day_now.lower())

                # если время совпадает с текущим, добавляем в список на отправ
                print(user_day_time)
                if user_day_time and f'{hours_now}:{minutes_now}' in user_day_time:
                    chat_id = reminder['chat_id']
                    group = reminder['group']
                    notifications = reminder['notifications']

                    # определяем фактическое время пары (прибавляем к текущему времени время напоминания)
                    lesson_time = (time_now + timedelta(minutes=notifications)).strftime('%-H:%-M')
                    print(lesson_time)

                    users.append(
                        {'chat_id': chat_id,
                         'group': group,
                         'week': week,
                         'day': day_now,
                         'notifications': notifications,
                         'time': lesson_time
                         }
                    )

            # после того как список сформирован, нужно отправить его боту
            print(users)
            sending_notifications(users)

            # записываем статистку
            date_now = datetime.now(TZ_IRKUTSK).strftime('%d.%m.%Y')
            time_now = datetime.now(TZ_IRKUTSK).strftime('%H:%M')
            storage.save_status_reminders_vk(date=date_now, time=time_now)


if __name__ == '__main__':
    search_for_reminders()
