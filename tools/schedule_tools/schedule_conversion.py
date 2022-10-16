TYPE_OF_LESSON = {
    1: 'Лекция',
    2: 'Практика',
    3: 'Лабораторная работа'
}


def convert_lessons_group(schedule_list: list) -> list:
    format_schedule_list = []

    for day in schedule_list:
        format_day = f'{day["day_of_week"]}\n\n'

        for lesson in day['lessons']:
            format_day += f'\t{lesson["lesson_start"]} - {lesson["lesson_end"]}\n'

            if lesson['lesson_type'] is not None and lesson['lesson_type'] != 0:
                format_day += f'\t{TYPE_OF_LESSON[lesson["lesson_type"]]}\n'

            format_day += f' - {lesson["name"]}\n'

            for teacher in lesson['teacher_fullname']:
                if teacher is not None and teacher != '':
                    format_day += f'{teacher}\n'

            if lesson['classroom'] is not None and lesson['classroom'] != '':
                format_day += f'Aудитория: {lesson["classroom"]}\n'

            if lesson['subgroup'] is not None and lesson['subgroup'] != 0:
                format_day += f'Подгруппа {lesson["subgroup"]}\n'

            format_day += '\n'

        format_schedule_list.append(format_day)

    return format_schedule_list


def convert_exams():
    pass
