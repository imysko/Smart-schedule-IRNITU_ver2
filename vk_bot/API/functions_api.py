import os

import requests

FUNCTIONS_API_URL = os.environ.get('FUNCTIONS_API_URL')


def get_api_data(url: str, data: dict):
    answer = requests.get(url=FUNCTIONS_API_URL + url, json=data)
    json_answer = answer.json()
    return json_answer


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
