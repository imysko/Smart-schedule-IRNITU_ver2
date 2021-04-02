import json
import os
import requests
from tools.storage import MongodbService

storage = MongodbService().get_instance()

JSON_EXAMS = os.environ.get('EXAMS')


def groups_exam(group, chat_id):
    try:
        response = requests.get(JSON_EXAMS)
    except requests.exceptions.ConnectionError:
        response.status_code = "Connection refused"

    json_data = json.loads(response.text)

    exam_group = json_data[group]['exams']

    clear_list = []

    for i in range(len(exam_group)):

        if exam_group[i] not in clear_list:
            clear_list.append(exam_group[i])

    storage.save_or_update_vk_user(chat_id=chat_id, exams=clear_list)

    return clear_list
