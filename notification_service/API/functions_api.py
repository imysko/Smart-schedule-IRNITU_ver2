import os

import requests

FUNCTIONS_API_URL = os.environ.get('FUNCTIONS_API_URL')


def get_api_data(url: str, data: dict = {}):
    answer = requests.get(url=FUNCTIONS_API_URL + url, json=data, verify=False)
    json_answer = answer.json()

    return json_answer


def calculating_reminder_times(schedule, time: int) -> list:
    """Прощитывает время уведомления перед кадой парой"""
    url = 'notifications/calculating_reminder_times/'
    data = {
        'schedule': schedule,
        'time': time,
    }
    reminders = get_api_data(url=url, data=data)
    return reminders


class APIError:
    def __init__(self, error_msg=None):
        self.error_msg = error_msg
