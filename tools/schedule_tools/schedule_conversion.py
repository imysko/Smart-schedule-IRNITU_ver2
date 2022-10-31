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
            format_day += format_lesson_group(lesson)

        format_schedule_list.append(format_day)

    return format_schedule_list


def format_lesson_group(lesson) -> str:
    format_day = f'\t{lesson["lesson_start"]} - {lesson["lesson_end"]}\n'
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
    format_day += '\n-------------------------------------------\n'
    return format_day


def convert_lessons_teachers(schedule_list: list) -> list:
    format_schedule_list = []

    for day in schedule_list:
        format_day = f'🍎{day["day_of_week"]}🍎'
        format_day += '\n-------------------------------------------\n'

        for lesson in day['lessons']:
            format_day += format_lesson_teacher(lesson)

        format_schedule_list.append(format_day)

    return format_schedule_list


def format_lesson_teacher(lesson) -> str:
    format_day = f'\t{lesson["lesson_start"]} - {lesson["lesson_end"]}\n'
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
    return format_day


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


def convert_lessons_reminder(lessons) -> str:
    lessons_for_reminders = ''

    count = 0
    for lesson in lessons:
        lessons_for_reminders += '-------------------------------------------\n'
        lessons_for_reminders += f'Начало в {lesson["lesson_start"]}\n'
        if lesson['lesson_type'] is not None and lesson['lesson_type'] != 0:
            lessons_for_reminders += f'{TYPE_OF_LESSON[lesson["lesson_type"]]}\n'
        lessons_for_reminders += f'👉{lesson["name"]}\n'
        auditory = lesson['classroom']
        if auditory:
            lessons_for_reminders += f'Аудитория: {auditory}\n'
        if lesson['subgroup'] is not None and lesson['subgroup'] != 0:
            lessons_for_reminders += f'Подгруппа {lesson["subgroup"]}\n'
        if lesson['teacher_fullname'][0] is not None:
            lessons_for_reminders += ', '.join(lesson['teacher_fullname'])
            lessons_for_reminders += '\n'
        count += 1

    if count > 0:
        lessons_for_reminders += '-------------------------------------------\n'

    return lessons_for_reminders


def convert_current_lessons_group(lessons_list: list) -> str:
    format_lessons = ''

    for lesson in lessons_list:
        format_lessons += format_lesson_group(lesson)

    return format_lessons


def convert_current_lessons_teacher(lessons_list: list) -> str:
    format_lessons = ''

    for lesson in lessons_list:
        format_lessons += format_lesson_teacher(lesson)

    return format_lessons


def convert_near_lessons_group(lessons: dict) -> str:
    format_lessons = f'🍎{lessons["day_of_week"]}🍎'
    format_lessons += '\n-------------------------------------------\n'

    print(lessons)
    for lesson in lessons['lessons']:
        format_lessons += format_lesson_group(lesson)

    return format_lessons


def convert_near_lessons_teacher(lessons: dict) -> str:
    format_lessons = f'🍎{lessons["day_of_week"]}🍎'
    format_lessons += '\n-------------------------------------------\n'

    for lesson in lessons['lessons']:
        format_lessons += format_lesson_teacher(lesson)

    return format_lessons
