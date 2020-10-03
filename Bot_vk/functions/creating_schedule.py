from datetime import datetime
import pytz
import locale

TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk')
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')


def full_schedule_in_str(schedule: list, week: str) -> list:
    schedule_str = []
    for one_day in schedule:
        day = one_day['day']
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
                info = lesson['info']
                prep = lesson['prep']

                lessons_str += f'{time}\n' \
                               f'{aud}' \
                               f'{name}\n' \
                               f'{info} {prep}'
            lessons_str += '\n-------------------------------------------\n'

        schedule_str.append(f'\n{day}\n'
                            f'{lessons_str}')

    return schedule_str


def get_one_day_schedule_in_str(schedule: list, week: str) -> str:
    day_now = datetime.now(TZ_IRKUTSK).strftime('%A')
    for one_day in schedule:
        day = one_day['day']
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
                    info = lesson['info']
                    prep = lesson['prep']

                    lessons_str += f'{time}\n' \
                                   f'{aud}' \
                                   f'{name}\n' \
                                   f'{info} {prep}'
                lessons_str += '\n-------------------------------------------\n'

            return f'\n{day}\n{lessons_str}'
