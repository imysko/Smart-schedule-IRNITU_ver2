import json
import os
import requests
from tg_bot.tools.storage import MongodbService


def exam_update():
    storage = MongodbService().get_instance()
    print(11)
    storage.delete_exam()

    JSON_EXAMS = os.environ.get('EXAMS_API')

    try:
        response = requests.get(JSON_EXAMS)
    except requests.exceptions.ConnectionError:
        response.status_code = "Connection refused"

    json_data = json.loads(response.text)

    schedule_exams = [{'group': a, 'exams': d} for a, d in json_data.items()]
    print(schedule_exams)
    storage.save_schedule_exam(schedule_exams)

exam_update()
