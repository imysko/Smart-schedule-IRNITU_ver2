import os

import requests

FUNCTIONS_API_URL = os.environ.get('FUNCTIONS_API_URL')


def get_api_data(url: str, data: dict = {}):
    answer = requests.get(url=FUNCTIONS_API_URL + url, json=data)
    json_answer = answer.json()
    return json_answer


def find_week():
    url = 'find_week/'
    week = get_api_data(url=url)

    return week


def full_schedule_in_str(schedule: list, week: str) -> list:
    url = 'creating_schedule/full_schedule_in_str/'
    data = {
        'schedule': schedule,
        'week': week
    }
    schedule_str = get_api_data(url=url, data=data)
    return schedule_str


def get_one_day_schedule_in_str(schedule: list, week: str) -> str:
    url = 'creating_schedule/get_one_day_schedule_in_str/'
    data = {
        'schedule': schedule,
        'week': week
    }
    one_day = get_api_data(url=url, data=data)

    return one_day


def get_next_day_schedule_in_str(schedule: list, week: str) -> str:
    url = 'creating_schedule/get_next_day_schedule_in_str/'
    data = {
        'schedule': schedule,
        'week': week
    }
    next_day = get_api_data(url=url, data=data)
    return next_day


# Расписание для преподавателей
def get_one_day_schedule_in_str_prep(schedule: list, week: str) -> str:
    url = 'creating_schedule/get_one_day_schedule_in_str_prep/'
    data = {
        'schedule': schedule,
        'week': week
    }
    one_day = get_api_data(url=url, data=data)
    return one_day


def get_next_day_schedule_in_str_prep(schedule: list, week: str) -> str:
    url = 'creating_schedule/get_next_day_schedule_in_str_prep/'
    data = {
        'schedule': schedule,
        'week': week
    }
    next_day = get_api_data(url=url, data=data)
    return next_day


def full_schedule_in_str_prep(schedule: list, week: str, aud=None) -> list:
    url = 'creating_schedule/full_schedule_in_str_prep/'
    data = {
        'schedule': schedule,
        'week': week,
        'aud': aud
    }
    schedule_str = get_api_data(url=url, data=data)
    return schedule_str


def get_near_lesson(schedule: list, week: str) -> list:
    """Возвращает ближайшую пару"""
    url = 'near_lesson/get_near_lesson/'
    data = {
        'schedule': schedule,
        'week': week,
    }
    near_lessons = get_api_data(url=url, data=data)

    return near_lessons


def get_now_lesson(schedule: list, week: str) -> list:
    """"Возвращает текущую пару"""
    url = 'near_lesson/get_now_lesson/'
    data = {
        'schedule': schedule,
        'week': week,
    }
    now_lessons = get_api_data(url=url, data=data)

    return now_lessons


def calculating_reminder_times(schedule, time: int) -> list:
    """Прощитывает время уведомления перед кадой парой"""
    url = 'notifications/calculating_reminder_times/'
    data = {
        'schedule': schedule,
        'time': time,
    }
    reminders = get_api_data(url=url, data=data)
    return reminders


def get_notifications_status(time):
    """Статус напоминаний"""
    url = 'notifications/get_notifications_status/'
    data = {
        'time': time
    }
    notifications_status = get_api_data(url=url, data=data)

    return notifications_status
