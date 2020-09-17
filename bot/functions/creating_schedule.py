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
                lessons_str += f'<b>{time}</b>\n' \
                               f'{name}'

            else:
                aud = lesson['aud']
                if aud:
                    aud = f'Аудитория: {aud}\n'
                time = lesson['time']
                info = lesson['info']
                prep = lesson['prep']

                lessons_str += f'<b>{time}</b>\n' \
                               f'{aud}' \
                               f'{name}\n' \
                               f'{info} {prep}'
            lessons_str += '\n-------------------------------------------\n'

        schedule_str.append(f'\n<b>{day}</b>\n'
                            f'{lessons_str}')

    return schedule_str
