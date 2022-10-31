import json
import os
import pathlib
from pathlib import Path

from db.api import data_conversion_api, postgre_storage_api
from tools.logger import logger


async def processing_api(bot, message):
    chat_id = message.chat.id
    text = message.text

    response = '{"null": "0"}'
    file_name = 'response.json'

    try:
        match text:
            case '/api/institutes':
                file_name = 'institutes.json'
                response = data_conversion_api.convert_institutes_dict(postgre_storage_api.get_institutes())
            case '/api/groups':
                file_name = 'groups.json'
                response = data_conversion_api.convert_groups_dict(postgre_storage_api.get_groups())
            case '/api/lessons_time':
                file_name = 'lessons_time.json'
                response = data_conversion_api.convert_lessons_dict(postgre_storage_api.get_lessons())
            case '/api/teachers':
                file_name = 'teachers.json'
                response = data_conversion_api.convert_teachers_dict(postgre_storage_api.get_teachers())
            case '/api/lessons_names':
                file_name = 'lessons_names.json'
                response = data_conversion_api.convert_disciplines_dict(postgre_storage_api.get_disciplines())
            case '/api/classrooms':
                file_name = 'schedule_year.json'
                response = data_conversion_api.convert_classrooms_dict(postgre_storage_api.get_classrooms())
            case '/api/schedule/two_weeks':
                file_name = 'schedule_two_weeks.json'
                response = data_conversion_api.convert_schedule_dict(postgre_storage_api.get_schedule())
            case '/api/schedule/year':
                file_name = 'schedule_year.json'
                response = data_conversion_api.convert_schedule_dict(postgre_storage_api.get_schedule_month())

        current_dir = pathlib.Path().resolve()

        Path(f'{current_dir}/api_responses/{chat_id}').mkdir(parents=True, exist_ok=True)
        file = open(f'{current_dir}/api_responses/{chat_id}/{file_name}', 'w')
        file.write(json.dumps(response, ensure_ascii=False))
        file.close()

        bot.send_document(
            chat_id=chat_id,
            document=open(f'{current_dir}/api_responses/{chat_id}/{file_name}'),
            timeout=90
        )
        os.remove(f'{current_dir}/api_responses/{chat_id}/{file_name}')
    except ValueError as error:
        logger.error(error)
