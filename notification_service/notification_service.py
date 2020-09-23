import time
import pytz
import locale

from datetime import datetime, timedelta

TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk')
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')


def find_week():
    now = datetime.now()
    sep = datetime(now.year if now.month >= 9 else now.year - 1, 9, 1)
    d1 = sep - timedelta(days=sep.weekday())
    d2 = now - timedelta(days=now.weekday())

    parity = ((d2 - d1).days // 7) % 2
    return 'odd' if parity else 'even'

# это будет формировать бот и записывать в базу данных
reminders = [
    {'chat_id': 99999999,
     'notifications': 15,
     'reminders': {
         'even':
             {
                 'понедельник': ['10:00', '13:00'],
                 'среда': ['19:00', f"20:{int(datetime.now(TZ_IRKUTSK).strftime('%M'))}"]
             },
         'odd':
             {
                 'вторник': ['11:25', '13:40'],
                 'среда': ['19:00', f"20:{int(datetime.now(TZ_IRKUTSK).strftime('%M'))}"]
             }
     }
     }
]

print(find_week())

minutes_old = None
while True:
    # определяем время сейчас
    time_now = datetime.now(TZ_IRKUTSK)
    day_now = datetime.now(TZ_IRKUTSK).strftime('%A').lower()
    hours_now = int(time_now.strftime('%H'))
    minutes_now = int(time_now.strftime('%M'))
    # отправлять сообщения нужно не раньше чем каждые 5 минут
    if minutes_now % 5 == 0 and minutes_old != minutes_now:
        minutes_old = minutes_now  # нужно для того чтобы выполнить тело только один раз
        users = []

        # сдесь нужно сходить в базу и забрать всех пользователей у который notifications != 0 или None

        for reminder in reminders:
            week = find_week()
            print(reminder['reminders'][week][day_now], f'{hours_now}:{minutes_now}')
            # если время совпадает с текущим, добавляем в список на отправку
            if f'{hours_now}:{minutes_now}' in reminder['reminders'][week][day_now.lower()]:
                users.append(
                    {'chat_id': reminder['chat_id'],
                     'week': week,
                     'day': day_now,
                     # определяем фактическое время пары (прибавляем к текущему времени время напоминания)
                     'time': (time_now + timedelta(minutes=reminder['notifications'])).strftime('%H:%M')
                     }
                )
        # послу того как список сформирован, нужно отправить его боту как json
        print(users)
