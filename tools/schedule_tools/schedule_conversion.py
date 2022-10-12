TYPE_OF_LESSON = {
    0: None,
    1: 'лекция',
    2: 'практика',
    3: 'лабораторная работа'
}


def convert_lessons(schedule_list: list) -> list:
    format_schedule_list = []

    for day in schedule_list:
        format_day = \
            f'{day["date"]}\n' \
            f'{day["day_of_week"]}\n'

        for lesson in day['lessons']:
            # - {TYPE_OF_LESSON[lesson["lesson_type"]]}
            format_day += \
                f'\t{lesson["lesson_number"]} - {TYPE_OF_LESSON[lesson["lesson_type"]]}\n' \
                f'\t{lesson["lesson_start"]}-{lesson["lesson_end"]}\n' \
                f'{lesson["name"]}\n' \
                f'{lesson["teacher_fullname"]}\n' \
                f'Аудитория: {lesson["classroom"]}\n' \
                f'Подгруппа {lesson["subgroup"]}\n'

        format_schedule_list.append(format_day)

    return format_schedule_list


def convert_lesson():
    pass


def convert_exams():
    pass
