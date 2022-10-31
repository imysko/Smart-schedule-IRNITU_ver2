import copy
import re

from db import postgre_storage
from datetime import timedelta, datetime

DAY_OF_WEEK = {
    1: 'Понедельник',
    2: 'Вторник',
    3: 'Среда',
    4: 'Четверг',
    5: 'Пятница',
    6: 'Суббота',
    7: 'Воскресенье'
}


def schedule_group_by_date(pg_schedule: list) -> list:
    schedule_list = []

    for record in pg_schedule:
        date = (record['dbeg'] + timedelta(days=(record['day'] - 1)))
        day = DAY_OF_WEEK[record['day']]

        del record['dbeg']
        del record['day']

        if not any(item['date'] == date for item in schedule_list):
            schedule_list.append({
                'date': date,
                'day_of_week': day,
                'lessons': [record]
            })
        else:
            next(item for item in schedule_list if item['date'] == date)['lessons'].append(record)

    return schedule_list


def __compare_lessons_without_teachers(first_lesson: dict, second_lesson: dict) -> bool:
    return first_lesson['lesson_number'] == second_lesson['lesson_number'] and \
           first_lesson['lesson_start'] == second_lesson['lesson_start'] and \
           first_lesson['lesson_end'] == second_lesson['lesson_end'] and \
           first_lesson['name'] == second_lesson['name'] and \
           first_lesson['list_group'] == second_lesson['list_group'] and \
           first_lesson['classroom'] == second_lesson['classroom'] and \
           first_lesson['lesson_type'] == second_lesson['lesson_type'] and \
           first_lesson['subgroup'] == second_lesson['subgroup']


def __compare_lessons_without_groups(first_lesson: dict, second_lesson: dict) -> bool:
    return first_lesson['lesson_number'] == second_lesson['lesson_number'] and \
           first_lesson['lesson_start'] == second_lesson['lesson_start'] and \
           first_lesson['lesson_end'] == second_lesson['lesson_end'] and \
           first_lesson['name'] == second_lesson['name'] and \
           first_lesson['teacher_fullname'] == second_lesson['teacher_fullname'] and \
           first_lesson['classroom'] == second_lesson['classroom'] and \
           first_lesson['lesson_type'] == second_lesson['lesson_type'] and \
           first_lesson['subgroup'] == second_lesson['subgroup']


def schedule_group_by_teachers(schedule_list: list) -> list:
    for day in schedule_list:
        without_changed_list = copy.deepcopy(day['lessons'])
        for lesson in day['lessons']:
            match = list(filter(lambda x: __compare_lessons_without_teachers(x, lesson), without_changed_list))
            teachers_list = list(map(lambda x: x['teacher_fullname'], match))

            lesson['teacher_fullname'] = teachers_list

        without_changed_list = copy.deepcopy(day['lessons'])
        day['lessons'].clear()
        for dictionary in without_changed_list:
            if dictionary not in day['lessons']:
                day['lessons'].append(dictionary)

    return schedule_list


def schedule_group_by_groups(schedule_list: list) -> list:
    for day in schedule_list:
        without_changed_list = copy.deepcopy(day['lessons'])
        for lesson in day['lessons']:
            match = list(filter(lambda x: __compare_lessons_without_groups(x, lesson), without_changed_list))
            groups_list = list(map(lambda x: x['list_group'], match))

            lesson['list_group'] = groups_list

        without_changed_list = copy.deepcopy(day['lessons'])
        day['lessons'].clear()
        for dictionary in without_changed_list:
            if dictionary not in day['lessons']:
                day['lessons'].append(dictionary)

    return schedule_list


def drop_current_teachers(schedule_list: list, teacher_id: int) -> list:
    teachers_list = postgre_storage.get_teachers()
    for day in schedule_list:
        for lesson in day['lessons']:
            current_teacher = next(x for x in teachers_list if x['teacher_id'] == teacher_id)['fullname']
            lesson['teacher_fullname'].remove(current_teacher)

    return schedule_list


def convert_schedule(pg_schedule: list,
                     next_week: bool = False,
                     selected_date: datetime = None) -> list:

    if not pg_schedule:
        raise ValueError('Данные не могут быть пустыми')

    for lesson in pg_schedule:
        lesson['name'] = cleanhtml(lesson['name'])

    if selected_date is not None:
        schedule_list = schedule_group_by_date(pg_schedule)
        schedule_list = list(filter(lambda x: x['date'] == selected_date.date(), schedule_list))
    else:
        if not next_week:
            start_of_week = pg_schedule[0]['dbeg']
        else:
            start_of_week = pg_schedule[-1]['dbeg']

        schedule_list = list(filter(lambda x: x['dbeg'] == start_of_week, pg_schedule))
        schedule_list = schedule_group_by_date(schedule_list)

    return schedule_list


def cleanhtml(html_str: str):
    regex = re.compile('<img.*?></img>')
    cleantext = re.sub(regex, '', html_str)
    return cleantext
