from datetime import datetime, timedelta
import platform
import locale
import pytz

TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk')
# определяем на Linux или на Windows мы запускаемся
locale_name = ('ru_RU.UTF-8' if platform.system() == 'Linux' else 'ru_RU')
locale.setlocale(locale.LC_TIME, locale_name)


def full_schedule_in_str(schedule: list, week: str) -> list:
    schedule_str = []
    day_now = datetime.now(TZ_IRKUTSK).strftime('%A').lower()
    for one_day in schedule:
        day = one_day['day'].upper()
        lessons = one_day['lessons']
        lessons_str = '-------------------------------------------\n'
        for lesson in lessons:
            name = lesson['name']
            time = lesson['time']
            lesson_week = lesson['week']

            # смотрим только на пары из нужной недели
            if lesson_week != week and lesson_week != 'all':
                continue

            if name == 'свободно':
                lessons_str += f'{time}\n' \
                               f'{name}'

            else:

                aud = lesson['aud']
                if aud:
                    aud = f'Аудитория: {aud}\n'
                time = lesson['time']
                info = lesson['info'].replace(",", "")
                prep = lesson['prep']

                lessons_str += f'{time}\n' \
                               f'{aud}' \
                               f'👉{name}\n' \
                               f'{info} {prep}'

            lessons_str += '\n-------------------------------------------\n'

        if day_now == day.lower():
            schedule_str.append(f'\n🍏{day}🍏\n'
                                f'{lessons_str}')
        else:
            schedule_str.append(f'\n🍎{day}🍎\n'
                                f'{lessons_str}')

    return schedule_str


def get_one_day_schedule_in_str(schedule: list, week: str) -> str:
    day_now = datetime.now(TZ_IRKUTSK).strftime('%A')
    for one_day in schedule:
        day = one_day['day'].upper()
        if day.lower() == day_now.lower():
            lessons = one_day['lessons']

            lessons_str = '-------------------------------------------\n'
            for lesson in lessons:
                name = lesson['name']
                time = lesson['time']
                lesson_week = lesson['week']

                # смотрим только на пары из нужной недели
                if lesson_week != week and lesson_week != 'all':
                    continue

                if name == 'свободно':
                    lessons_str += f'{time}\n' \
                                   f'{name}'

                else:
                    aud = lesson['aud']
                    if aud:
                        aud = f'Аудитория: {aud}\n'
                    time = lesson['time']
                    info = lesson['info'].replace(",", "")
                    prep = lesson['prep']

                    lessons_str += f'{time}\n' \
                                   f'{aud}' \
                                   f'👉{name}\n' \
                                   f'{info} {prep}'
                lessons_str += '\n-------------------------------------------\n'

            return f'\n🍏{day}🍏\n{lessons_str}'


def get_next_day_schedule_in_str(schedule: list, week: str) -> str:
    day_tomorrow = (datetime.now(TZ_IRKUTSK) + timedelta(days=1)).strftime('%A')
    for one_day in schedule:
        day = one_day['day'].upper()
        if day.lower() == day_tomorrow.lower():
            lessons = one_day['lessons']

            lessons_str = '-------------------------------------------\n'
            for lesson in lessons:
                name = lesson['name']
                time = lesson['time']
                lesson_week = lesson['week']

                # смотрим только на пары из нужной недели
                if lesson_week != week and lesson_week != 'all':
                    continue

                if name == 'свободно':
                    lessons_str += f'{time}\n' \
                                   f'{name}'

                else:
                    aud = lesson['aud']
                    if aud:
                        aud = f'Аудитория: {aud}\n'
                    time = lesson['time']
                    info = lesson['info'].replace(",", "")
                    prep = lesson['prep']

                    lessons_str += f'{time}\n' \
                                   f'{aud}' \
                                   f'👉{name}\n' \
                                   f'{info} {prep}'
                lessons_str += '\n-------------------------------------------\n'

            return f'\n🍎{day}🍎\n{lessons_str}'


# Расписание для преподавателей
def get_one_day_schedule_in_str_prep(schedule: list, week: str) -> str:
    day_now = datetime.now(TZ_IRKUTSK).strftime('%A')
    for one_day in schedule:
        day = one_day['day'].upper()
        if day.lower() == day_now.lower():
            lessons = one_day['lessons']

            lessons_str = '-------------------------------------------\n'
            for lesson in lessons:
                name = lesson['name']
                time = lesson['time']
                lesson_week = lesson['week']

                # смотрим только на пары из нужной недели
                if lesson_week != week and lesson_week != 'all':
                    continue

                if name == 'свободно':
                    lessons_str += f'{time}\n' \
                                   f'{name}'

                else:
                    aud = lesson['aud']
                    if aud:
                        aud = f'Аудитория: {aud}\n'
                    time = lesson['time']
                    info = lesson['info'].replace(",", "")

                    lessons_str += f'{time}\n' \
                                   f'{aud}' \
                                   f'👉{name}\n' \
                                   f'{info}'
                lessons_str += '\n-------------------------------------------\n'

            return f'\n🍏{day}🍏\n{lessons_str}'


def get_next_day_schedule_in_str_prep(schedule: list, week: str) -> str:
    day_tomorrow = (datetime.now(TZ_IRKUTSK) + timedelta(days=1)).strftime('%A')
    for one_day in schedule:
        day = one_day['day'].upper()
        if day.lower() == day_tomorrow.lower():
            lessons = one_day['lessons']

            lessons_str = '-------------------------------------------\n'
            for lesson in lessons:
                name = lesson['name']
                time = lesson['time']
                lesson_week = lesson['week']

                # смотрим только на пары из нужной недели
                if lesson_week != week and lesson_week != 'all':
                    continue

                if name == 'свободно':
                    lessons_str += f'{time}\n' \
                                   f'{name}'

                else:
                    aud = lesson['aud']
                    if aud:
                        aud = f'Аудитория: {aud}\n'
                    time = lesson['time']
                    info = lesson['info'].replace(",", "")

                    lessons_str += f'{time}\n' \
                                   f'{aud}' \
                                   f'👉{name}\n' \
                                   f'{info}'
                lessons_str += '\n-------------------------------------------\n'

            return f'\n🍎{day}🍎\n{lessons_str}'


def full_schedule_in_str_prep(schedule: list, week: str) -> list:
    schedule_str = []
    day_now = datetime.now(TZ_IRKUTSK).strftime('%A').lower()
    for one_day in schedule:
        day = one_day['day'].upper()
        lessons = one_day['lessons']
        lessons_str = '-------------------------------------------\n'
        for lesson in lessons:
            name = lesson['name']
            time = lesson['time']
            lesson_week = lesson['week']

            # смотрим только на пары из нужной недели
            if lesson_week != week and lesson_week != 'all':
                continue

            if name == 'свободно':
                lessons_str += f'{time}\n' \
                               f'{name}'

            else:

                aud = lesson['aud']
                if aud:
                    aud = f'Аудитория: {aud}\n'
                time = lesson['time']
                info = lesson['info'].replace(",", "")

                lessons_str += f'{time}\n' \
                               f'{aud}' \
                               f'👉{name}\n' \
                               f'{info}'

            lessons_str += '\n-------------------------------------------\n'

        if day_now == day.lower():
            schedule_str.append(f'\n🍏{day}🍏\n'
                                f'{lessons_str}')
        else:
            schedule_str.append(f'\n🍎{day}🍎\n'
                                f'{lessons_str}')

    return schedule_str
