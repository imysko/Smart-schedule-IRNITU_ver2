import pytz
import locale
import os
import telebot
from datetime import datetime, timedelta
from storage import MongodbService

import platform

TOKEN = os.environ.get('TOKEN')
TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk')
locale_name = ('ru_RU.UTF-8' if platform.system() == 'Linux' else 'ru_RU')
locale.setlocale(locale.LC_TIME, locale_name)

bot = telebot.TeleBot(TOKEN, threaded=False)

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
            lesson_time = lesson['time']
            # находим нужные пары (в нужное время)
            if lesson_time == time and (lesson['week'] == week or lesson['week'] == 'all'):
                name = lesson['name']
                # пропускаем свободные дни
                if name == 'свободно':
                    continue
                # формируем сообщение
                lessons_for_reminders += '-------------------------------------------\n'
                aud = lesson['aud']
                if aud:
                    aud = f'Аудитория: {aud}\n'
                time = lesson['time']
                info = lesson['info']
                prep = lesson['prep']

                lessons_for_reminders += f'<b>Начало в {time}</b>\n' \
                                         f'{aud}' \
                                         f'{name}\n' \
                                         f'{info} {prep}\n'
                lessons_for_reminders += '-------------------------------------------\n'
        # если пары не нашлись переходим к след user
        if not lessons_for_reminders:
            continue
        # отправляем сообщение пользователю
        bot.send_message(chat_id=chat_id, text=f'<b>Через {notifications} минут пара</b>\n'
                                               f'{lessons_for_reminders}', parse_mode='HTML')
        # записываем статистку
        date_now = datetime.now(TZ_IRKUTSK).strftime('%d.%m.%Y')
        time_now = datetime.now(TZ_IRKUTSK).strftime('%H:%M')
        storage.save_status_tg(date=date_now, time=time_now)


def search_for_reminders():
    print('reminders_tg is started')
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
            reminders = storage.get_users_with_reminders()
            print(reminders)

            for reminder in reminders:
                week = find_week()

                # если у пользователя пустой reminders то None
                user_days = reminder['reminders'].get(week)
                if not user_days:
                    continue
                # если у пользователя нет ткущего дня, то None
                user_day_time = user_days.get(day_now.lower())

                # если время совпадает с текущим, добавляем в список на отправ
                if user_day_time and f'{hours_now}:{minutes_now}' in user_day_time:
                    chat_id = reminder['chat_id']
                    group = reminder['group']
                    notifications = reminder['notifications']

                    # определяем фактическое время пары (прибавляем к текущему времени время напоминания)
                    lesson_time = (time_now + timedelta(minutes=notifications)).strftime('%-H:%-M')

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


if __name__ == '__main__':
    search_for_reminders()
