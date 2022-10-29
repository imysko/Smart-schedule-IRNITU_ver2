from datetime import datetime, timedelta

import pendulum
import pytz

from db import data_conversion, postgre_storage
from tools.logger import logger

TIME_ZONE = pytz.timezone('Asia/Irkutsk')


def get_group_schedule(
        group_id: int,
        next_week: bool = False,
        selected_date: datetime = None) -> list:
    data_list = data_conversion.convert_schedule(
        pg_schedule=postgre_storage.get_schedule_by_group(group_id),
        next_week=next_week,
        selected_date=selected_date
    )

    data_list = data_conversion.schedule_group_by_teachers(data_list)

    return data_list


def get_teacher_schedule(
        teacher_id: int,
        next_week: bool = False,
        selected_date: datetime = None) -> list:
    data_list = data_conversion.convert_schedule(
        pg_schedule=postgre_storage.get_schedule_by_teacher(teacher_id),
        next_week=next_week,
        selected_date=selected_date
    )

    data_list = data_conversion.schedule_group_by_teachers(data_list)
    data_list = data_conversion.drop_current_teachers(data_list, teacher_id=teacher_id)
    data_list = data_conversion.schedule_group_by_groups(data_list)

    return data_list


def get_classroom_schedule(
        classroom_id: int,
        next_week: bool = False,
        selected_date: datetime = None) -> list:
    data_list = data_conversion.convert_schedule(
        pg_schedule=postgre_storage.get_schedule_by_classroom(classroom_id),
        next_week=next_week,
        selected_date=selected_date
    )

    data_list = data_conversion.schedule_group_by_teachers(data_list)
    logger.info(data_list)
    data_list = data_conversion.schedule_group_by_groups(data_list)
    logger.info(data_list)

    return data_list


def current_lesson(lesson: dict, datetime_now: datetime) -> bool:
    lesson_start_time = datetime.strptime(f'{str(datetime_now.date())} {lesson["lesson_start"]}', '%Y-%m-%d %H:%M')
    lesson_end_time = datetime.strptime(f'{str(datetime_now.date())} {lesson["lesson_end"]}', '%Y-%m-%d %H:%M')
    return TIME_ZONE.localize(lesson_start_time) <= datetime_now <= TIME_ZONE.localize(lesson_end_time)


def past_lesson(lesson: dict, datetime_now: datetime) -> bool:
    lesson_end_time = datetime.strptime(f'{str(datetime_now.date())} {lesson["lesson_end"]}', '%Y-%m-%d %H:%M')
    return TIME_ZONE.localize(lesson_end_time) >= datetime_now


def future_lesson(lesson: dict, datetime_now: datetime) -> bool:
    lesson_start_time = datetime.strptime(f'{str(datetime_now.date())} {lesson["lesson_start"]}', '%Y-%m-%d %H:%M')
    return datetime_now <= TIME_ZONE.localize(lesson_start_time)


def get_group_current_lesson(group_id: int) -> list:
    datetime_now = datetime.now(TIME_ZONE)

    schedule_list = get_group_schedule(
        group_id=group_id,
        selected_date=datetime_now
    )

    lessons_list = []
    if len(schedule_list):
        lessons_list = list(filter(lambda lesson: current_lesson(lesson, datetime_now), schedule_list[0]['lessons']))

    return lessons_list


def get_group_near_lesson(group_id: int) -> dict:
    datetime_now = datetime.now(TIME_ZONE)

    schedule_list = get_group_schedule(group_id=group_id, next_week=False)
    schedule_list += get_group_schedule(group_id=group_id, next_week=True)

    # фильтруем уже прошедшие дни
    schedule_list = list(filter(lambda date: date['date'] >= datetime_now.date(), schedule_list))

    # фильтруем уже прошедшие пары
    lessons_list = list(filter(lambda lesson: past_lesson(lesson, datetime_now), schedule_list[0]['lessons']))
    # фильтруем ещё не прошедшие пары
    lessons_list = list(filter(lambda lesson: future_lesson(lesson, datetime_now), lessons_list))

    lessons = None
    # если все пары сегодня прошли то следующий день
    if len(lessons_list):
        # фильтруем одинаковые пары
        lessons_list = list(filter(
            lambda lesson: lesson['lesson_number'] == lessons_list[0]['lesson_number'], lessons_list))
        lessons = {
            'date': schedule_list[0]['date'],
            'day_of_week': schedule_list[0]['day_of_week'],
            'lessons': lessons_list
        }
    elif len(schedule_list) > 1:
        # фильтруем одинаковые пары
        lessons_list = list(filter(
            lambda lesson: lesson['lesson_number'] == schedule_list[1]['lessons'][0]['lesson_number'],
            schedule_list[1]['lessons']))
        lessons = {
            'date': schedule_list[1]['date'],
            'day_of_week': schedule_list[1]['day_of_week'],
            'lessons': lessons_list
        }

    return lessons


def get_teacher_current_lesson(teacher_id: int) -> list:
    datetime_now = datetime.now(TIME_ZONE)

    schedule_list = get_teacher_schedule(
        teacher_id=teacher_id,
        selected_date=datetime_now
    )

    lessons_list = []
    if len(schedule_list):
        lessons_list = list(filter(lambda lesson: current_lesson(lesson, datetime_now), schedule_list[0]['lessons']))

    return lessons_list


def get_teacher_near_lesson(teacher_id: int) -> dict:
    datetime_now = datetime.now(TIME_ZONE)

    schedule_list = get_teacher_schedule(teacher_id=teacher_id, next_week=False)
    schedule_list += get_teacher_schedule(teacher_id=teacher_id, next_week=True)

    # фильтруем уже прошедшие дни
    schedule_list = list(filter(lambda date: date['date'] >= datetime_now.date(), schedule_list))

    # фильтруем уже прошедшие пары
    lessons_list = list(filter(lambda lesson: past_lesson(lesson, datetime_now), schedule_list[0]['lessons']))
    # фильтруем ещё не прошедшие пары
    lessons_list = list(filter(lambda lesson: future_lesson(lesson, datetime_now), lessons_list))

    lessons = None
    # если все пары сегодня прошли то следующий день
    if len(lessons_list):
        # фильтруем одинаковые пары
        lessons_list = list(filter(
            lambda lesson: lesson['lesson_number'] == lessons_list[0]['lesson_number'], lessons_list))
        lessons = {
            'day_of_week': schedule_list[0]['day_of_week'],
            'lessons': lessons_list
        }
    elif len(schedule_list) > 1:
        # фильтруем одинаковые пары
        lessons_list = list(filter(
            lambda lesson: lesson['lesson_number'] == schedule_list[1]['lessons'][0]['lesson_number'],
            schedule_list[1]['lessons']))
        lessons = {
            'day_of_week': schedule_list[1]['day_of_week'],
            'lessons': lessons_list
        }

    return lessons
