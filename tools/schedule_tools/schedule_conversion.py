TYPE_OF_LESSON = {
    1: 'Лекция',
    2: 'Практика',
    3: 'Лабораторная работа'
}


def convert_lessons_group(schedule_list: list) -> list:
    format_schedule_list = []

    for day in schedule_list:
        format_day = f'🍎{day["day_of_week"]}🍎'
        format_day += '\n-------------------------------------------\n'
        for lesson in day['lessons']:
            format_day += f'\t{lesson["lesson_start"]} - {lesson["lesson_end"]}\n'

            if lesson['lesson_type'] is not None and lesson['lesson_type'] != 0:
                format_day += f'\t{TYPE_OF_LESSON[lesson["lesson_type"]]}\n'

            format_day += f'👉{lesson["name"]}'

            for teacher in lesson['teacher_fullname']:
                if teacher is not None and teacher != '':
                    format_day += f'\n{teacher}'

            if lesson['classroom'] is not None and lesson['classroom'] != '':
                format_day += f'\nAудитория: {lesson["classroom"]}'

            if lesson['subgroup'] is not None and lesson['subgroup'] != 0:
                format_day += f'\nПодгруппа {lesson["subgroup"]}'

            format_day += '\n-------------------------------------------'

        format_schedule_list.append(format_day)

    return format_schedule_list


def convert_lessons_teachers(schedule_list: list) -> list:
    format_schedule_list = []

    for day in schedule_list:
        format_day = f'🍎{day["day_of_week"]}🍎'
        format_day += '\n-------------------------------------------\n'

        for lesson in day['lessons']:
            format_day += f'\t{lesson["lesson_start"]} - {lesson["lesson_end"]}\n'

            if lesson['lesson_type'] is not None and lesson['lesson_type'] != 0:
                format_day += f'\t{TYPE_OF_LESSON[lesson["lesson_type"]]}\n'

            format_day += f'👉{lesson["name"]}'

            for teacher in lesson['teacher_fullname']:
                if teacher is not None and teacher != '':
                    if len(lesson['teacher_fullname']) == 1:
                        format_day += f'\nДругой преподаватель: {teacher}'
                    else:
                        format_day += f'\nДругие преподаватели: {teacher}'

            if lesson['classroom'] is not None and lesson['classroom'] != '':
                format_day += f'\nAудитория: {lesson["classroom"]}'

            if len(lesson['list_group']):
                format_day += f'\nГруппы: ' \
                              f'{", ".join(group if group is not None else "" for group in lesson["list_group"][:3])}'
            if len(lesson["list_group"][3:]):
                format_day += f' + {len(lesson["list_group"][3:])} групп'

            if lesson['subgroup'] is not None and lesson['subgroup'] != 0:
                format_day += f'\nПодгруппа {lesson["subgroup"]}'

            format_day += '\n-------------------------------------------\n'

        format_schedule_list.append(format_day)

    return format_schedule_list


def convert_lessons_classrooms(schedule_list: list) -> list:
    format_schedule_list = []

    for day in schedule_list:
        format_day = f'🍎{day["day_of_week"]}🍎'
        format_day += '\n-------------------------------------------\n'

        for lesson in day['lessons']:
            format_day += f'\t{lesson["lesson_start"]} - {lesson["lesson_end"]}\n'

            if lesson['lesson_type'] is not None and lesson['lesson_type'] != 0:
                format_day += f'\t{TYPE_OF_LESSON[lesson["lesson_type"]]}\n'

            format_day += f'👉{lesson["name"]}'

            for teacher in lesson['teacher_fullname']:
                if teacher is not None and teacher != '':
                    format_day += f'\n{teacher}'

            if len(lesson['list_group']):
                format_day += f'\nГруппы: ' \
                              f'{", ".join(group if group is not None else "" for group in lesson["list_group"][:3])}'
            if len(lesson["list_group"][3:]):
                format_day += f' + {len(lesson["list_group"][3:])} групп'

            if lesson['subgroup'] is not None and lesson['subgroup'] != 0:
                format_day += f'\nПодгруппа {lesson["subgroup"]}'

            format_day += '\n-------------------------------------------\n'

        format_schedule_list.append(format_day)

    return format_schedule_list
