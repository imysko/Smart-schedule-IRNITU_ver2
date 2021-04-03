import json
import os
import requests
from vk_bot.tools.storage import MongodbService


def exam_update():
    storage = MongodbService().get_instance()

    storage.delete_exam()

    JSON_EXAMS = os.environ.get('EXAMS')

    try:
        response = requests.get(JSON_EXAMS)
    except requests.exceptions.ConnectionError:
        response.status_code = "Connection refused"

    json_data = json.loads(response.text)

    schedule_exams = [{'group': a, 'exams': d} for a, d in json_data.items()]

    storage.save_schedule_exam(schedule_exams)
