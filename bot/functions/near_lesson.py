from datetime import datetime
import pytz
import locale

TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk')
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')  #


def get_near_lesson(schedule: list, week: str) -> dict:
    """"Возвращает ближайшую пару"""

    day_now = datetime.now(TZ_IRKUTSK).strftime('%A')
    hours_now = int(datetime.now(TZ_IRKUTSK).strftime('%H'))
    minutes_now = int(datetime.now(TZ_IRKUTSK).strftime('%M'))

    lessons = {}
    # находим текущий день
    for one_day in schedule:
        if one_day['day'].lower() == day_now.lower():
            lessons = one_day['lessons']
            break
    # если сегодняшнего дня нет в расписании значит пар сегодня нет
    if not lessons:
        return

    for lesson in lessons:
        lesson_week = lesson['week']
        # смотрим только на пары из текущей недели
        if lesson_week != week and lesson_week != 'all':
            continue

        hours_lesson, minutes_lesson = map(int, lesson['time'].split(':'))
        # находим ближайшую пару
        if (hours_lesson * 60 + minutes_lesson) - (hours_now * 60 + minutes_now) >= 0:
            near_lesson = lesson
            return near_lesson


if __name__ == '__main__':
    schedule = [{'day': 'понедельник',
                 'lessons': [{'aud': '',
                              'info': '( Практ.,  )',
                              'name': 'Элективные курсы по физической культуре и спорту',
                              'prep': '',
                              'time': '8:15',
                              'week': 'even'},
                             {'aud': 'Ж309',
                              'info': '( Практ.,  )',
                              'name': 'Документоведение',
                              'prep': 'Иванов Н.А.',
                              'time': '8:15',
                              'week': 'odd'},
                             {'aud': 'ДАМФа',
                              'info': '( Практ.,  )',
                              'name': 'Цифровая обработка сигналов',
                              'prep': 'Дмитриев А. А.',
                              'time': '10:00',
                              'week': 'even'},
                             {'aud': 'Ж317',
                              'info': '( Практ.,  )',
                              'name': 'Теория информации',
                              'prep': 'Афанасьева Ж.С.',
                              'time': '10:00',
                              'week': 'odd'},
                             {'aud': 'И305',
                              'info': '( Лекция,  )',
                              'name': 'Математическая логика и теория алгоритмов',
                              'prep': 'Богданов А.И.',
                              'time': '11:45',
                              'week': 'all'},
                             {'aud': 'Ж309',
                              'info': '( Практ.,  )',
                              'name': 'Теория принятия решений',
                              'prep': 'Маринов А.А.',
                              'time': '13:45',
                              'week': 'all'},
                             {'aud': 'онлайн',
                              'info': '( Лекция,  )',
                              'name': 'Теория информации',
                              'prep': 'Афанасьев А.Д.',
                              'time': '17:10',
                              'week': 'even'},
                             {'aud': 'онлайн',
                              'info': '( Лекция,  )',
                              'name': 'Теория информации',
                              'prep': 'Афанасьев А.Д.',
                              'time': '17:10',
                              'week': 'odd'},
                             {'aud': 'онлайн',
                              'info': '( Практ., подгруппа 1 )',
                              'name': 'Иностранный язык в сфере профессиональной коммуникации',
                              'prep': '',
                              'time': '18:45',
                              'week': 'all'},
                             {'aud': 'онлайн',
                              'info': '( Практ., подгруппа 2 )',
                              'name': 'Иностранный язык в сфере профессиональной коммуникации',
                              'prep': '',
                              'time': '18:45',
                              'week': 'all'}]},
                {'day': 'среда',
                 'lessons': [{'aud': 'Ж313',
                              'info': '( Лаб. раб., подгруппа 1 )',
                              'name': 'Математические основы криптологии',
                              'prep': 'Тюрнев А.С.',
                              'time': '8:15',
                              'week': 'all'},
                             {'aud': 'ДАМФа',
                              'info': '( Лаб. раб., подгруппа 2 )',
                              'name': 'Цифровая обработка сигналов',
                              'prep': 'Дмитриев А. А.',
                              'time': '8:15',
                              'week': 'all'},
                             {'aud': 'ДАМФа',
                              'info': '( Лаб. раб., подгруппа 1 )',
                              'name': 'Цифровая обработка сигналов',
                              'prep': 'Дмитриев А. А.',
                              'time': '10:00',
                              'week': 'all'},
                             {'aud': 'Ж313',
                              'info': '( Лаб. раб., подгруппа 2 )',
                              'name': 'Математические основы криптологии',
                              'prep': 'Тюрнев А.С.',
                              'time': '10:00',
                              'week': 'all'},
                             {'aud': '',
                              'info': '( Практ.,  )',
                              'name': 'Элективные курсы по физической культуре и спорту',
                              'prep': '',
                              'time': '11:45',
                              'week': 'even'},
                             {'aud': '',
                              'info': '( Практ.,  )',
                              'name': 'Элективные курсы по физической культуре и спорту',
                              'prep': '',
                              'time': '11:45',
                              'week': 'odd'},
                             {'aud': 'И305',
                              'info': '( Лекция,  )',
                              'name': 'Теория принятия решений',
                              'prep': 'Маринов А.А.',
                              'time': '22:00',
                              'week': 'all'}]},
                {'day': 'четверг',
                 'lessons': [{'aud': 'И305',
                              'info': '( Лекция,  )',
                              'name': 'Документоведение',
                              'prep': 'Иванов Н.А.',
                              'time': '8:15',
                              'week': 'even'},
                             {'aud': 'Дамф.',
                              'info': '( Лекция,  )',
                              'name': 'Цифровая обработка сигналов',
                              'prep': 'Дмитриев А. А.',
                              'time': '8:15',
                              'week': 'odd'},
                             {'aud': 'И305',
                              'info': '( Практ.,  )',
                              'name': 'Математическая логика и теория алгоритмов',
                              'prep': 'Богданов А.И.',
                              'time': '10:00',
                              'week': 'all'},
                             {'aud': 'Ж317',
                              'info': '( Лекция,  )',
                              'name': 'Математические основы криптологии',
                              'prep': 'Тюрнев А.С.',
                              'time': '11:45',
                              'week': 'all'},
                             {'aud': 'Ж309',
                              'info': '( Практ.,  )',
                              'name': 'Математические основы криптологии',
                              'prep': 'Тюрнев А.С.',
                              'time': '13:45',
                              'week': 'all'}]},
                {'day': 'пятница',
                 'lessons': [{'aud': 'К313',
                              'info': '( Практ.,  )',
                              'name': 'Документоведение',
                              'prep': 'Иванов Н.А.',
                              'time': '8:15',
                              'week': 'even'},
                             {'name': 'свободно', 'time': '8:15', 'week': 'odd'},
                             {'aud': 'К305',
                              'info': '( Лекция,  )',
                              'name': 'Защита персональных данных (факультатив)',
                              'prep': 'Иванов Н.А.',
                              'time': '10:00',
                              'week': 'even'},
                             {'name': 'свободно', 'time': '10:00', 'week': 'odd'},
                             {'aud': 'Ж317',
                              'info': '( Практ.,  )',
                              'name': 'Защита персональных данных (факультатив)',
                              'prep': 'Иванов Н.А.',
                              'time': '11:45',
                              'week': 'even'},
                             {'name': 'свободно', 'time': '11:45', 'week': 'odd'}]}]
    print(get_near_lesson(schedule, 'even'))
