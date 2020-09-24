import pytz
import locale
import os
import telebot
from datetime import datetime, timedelta
from functions.storage import MongodbService

TOKEN = os.environ.get('TOKEN')
TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk')
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

bot = telebot.TeleBot(TOKEN, threaded=False)

storage = MongodbService().get_instance()


def find_week():
    now = datetime.now()
    sep = datetime(now.year if now.month >= 9 else now.year - 1, 9, 1)
    d1 = sep - timedelta(days=sep.weekday())
    d2 = now - timedelta(days=now.weekday())

    parity = ((d2 - d1).days // 7) % 2
    return 'odd' if parity else 'even'


# это будет формировать бот и записывать в базу данных
reminders = [
    {'chat_id': 891209550,
     'notifications': 15,
     'group': 'ИБб-18-1',
     'reminders': {
         'even':
             {
                 'понедельник': ['10:00', '13:00'],
                 'четверг': ['19:00', datetime.now(TZ_IRKUTSK).strftime('%-H:%-M')]
             },
         'odd':
             {
                 'вторник': ['11:25', '13:40'],
                 'четверг': ['19:00', datetime.now(TZ_IRKUTSK).strftime('%-H:%-M')]
             }
     }
     }
]

SCHEDULE = {"group": "ИБб-18-1", "schedule": [
    {"day": "понедельник", "lessons": [
        {"time": "8:15", "week": "even", "name": "Элективные курсы по физической культуре и спорту", "aud": "",
         "info": "( Практ.,  )", "prep": ""},
        {"time": "8:15", "week": "odd", "name": "Документоведение", "aud": "Ж309", "info": "( Практ.,  )",
         "prep": "Иванов Н.А."},
        {"time": "10:00", "week": "even", "name": "Цифровая обработка сигналов", "aud": "ДАМФа", "info": "( Практ.,  )",
         "prep": "Дмитриев А. А."},
        {"time": "10:00", "week": "odd", "name": "Теория информации", "aud": "Ж317", "info": "( Практ.,  )",
         "prep": "Афанасьева Ж.С."},
        {"time": "11:45", "week": "all", "name": "Математическая логика и теория алгоритмов", "aud": "И305",
         "info": "( Лекция,  )", "prep": "Богданов А.И."},
        {"time": "13:45", "week": "all", "name": "Теория принятия решений", "aud": "Ж309", "info": "( Практ.,  )",
         "prep": "Маринов А.А."},
        {"time": "18:45", "week": "all", "name": "Иностранный язык в сфере профессиональной коммуникации",
         "aud": "онлайн",
         "info": "( Практ., подгруппа 1 )", "prep": ""},
        {"time": "18:45", "week": "all", "name": "Иностранный язык в сфере профессиональной коммуникации",
         "aud": "онлайн",
         "info": "( Практ., подгруппа 2 )", "prep": ""}]},

    {"day": "четверг", "lessons": [
        {"time": "8:15", "week": "all",
         "name": "Математические основы криптологии", "aud": "Ж313",
         "info": "( Лаб. раб., подгруппа 1 )", "prep": "Тюрнев А.С."},
        {"time": (datetime.now(TZ_IRKUTSK) + timedelta(minutes=15)).strftime('%-H:%-M'), "week": "all",
         "name": "Цифровая обработка сигналов",
         "aud": "ДАМФа",
         "info": "( Лаб. раб., подгруппа 2 )", "prep": "Дмитриев А. А."},
        {"time": "10:00", "week": "all",
         "name": "Цифровая обработка сигналов", "aud": "ДАМФа",
         "info": "( Лаб. раб., подгруппа 1 )", "prep": "Дмитриев А. А."},
        {"time": "10:00", "week": "all",
         "name": "Математические основы криптологии", "aud": "Ж313",
         "info": "( Лаб. раб., подгруппа 2 )", "prep": "Тюрнев А.С."},
        {"time": "11:45", "week": "even",
         "name": "Элективные курсы по физической культуре и спорту",
         "aud": "",
         "info": "( Практ.,  )", "prep": ""},
        {"time": "11:45", "week": "odd",
         "name": "Элективные курсы по физической культуре и спорту",
         "aud": "",
         "info": "( Практ.,  )", "prep": ""},
        {"time": "13:45", "week": "all", "name": "Теория принятия решений",
         "aud": "И305", "info": "( Лекция,  )",
         "prep": "Маринов А.А."}]}]}


def sending_notifications(users: list):
    for user in users:
        chat_id = user['chat_id']
        week = user['week']
        day_now = user['day']
        time = user['time']
        group = user['group']
        notifications = user['notifications']

        # schedule = storage.get_schedule(group=group)['schedule']
        schedule = SCHEDULE['schedule']  # временно для отладки!!!!!!!

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
            # находим нужные пары (в нужное время)
            if lesson['time'] == time and (lesson['week'] == week or lesson['week'] == 'all'):
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


def search_for_reminders():
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

            # сдесь нужно сходить в базу и забрать всех пользователей у который notifications != 0 или None

            for reminder in reminders:
                week = find_week()
                # если время совпадает с текущим, добавляем в список на отправку
                # не всегда у пользователя есть нужный день!!!!!!!!!!! нужно добавит проверку
                if f'{hours_now}:{minutes_now}' in reminder['reminders'][week][day_now.lower()]:
                    chat_id = reminder['chat_id']
                    group = reminder['group']
                    notifications = reminder['notifications']
                    users.append(
                        {'chat_id': chat_id,
                         'group': group,
                         'week': week,
                         'day': day_now,
                         'notifications': notifications,
                         # определяем фактическое время пары (прибавляем к текущему времени время напоминания)
                         'time': (time_now + timedelta(minutes=notifications)).strftime('%-H:%-M')
                         }
                    )

            # после того как список сформирован, нужно отправить его боту
            print(users)
            sending_notifications(users)


if __name__ == '__main__':
    search_for_reminders()
