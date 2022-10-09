import traceback

from db.mongo_storage import MongodbService
from tools.logger import logger

import time
import os

import json
import requests

# Задержка работы цикла (в часах).
GETTING_SCHEDULE_TIME_HOURS = float(os.environ.get('GETTING_SCHEDULE_TIME_HOURS')
                                    if os.environ.get('GETTING_SCHEDULE_TIME_HOURS')
                                    else 1) * 60 * 60

mongo_storage = MongodbService().get_instance()


def exam_update():
    logger.info('Start processing_exams_schedule...')

    JSON_EXAMS = os.environ.get('EXAMS_API')

    try:
        response = requests.get(JSON_EXAMS)
        json_data = json.loads(response.text)
        schedule_exams = [{'group': a, 'exams': d}
                          for a, d in json_data.items()]
        mongo_storage.save_schedule_exam(schedule_exams)
        logger.info('End processing_exams_schedule...')

    except requests.exceptions.ConnectionError:
        logger.error("Error processing_exams_schedule: Connection refused")


def main():
    while True:
        # Время начала работы цикла.
        start_time = time.time()

        # Обновление базы экзаменов
        try:
            exam_update()
        except:
            traceback.print_exc()

        # Время окончания работы цикла.
        end_time = time.time()
        logger.info(f'Total operating time --- {end_time - start_time} seconds ---')

        # Задержка работы цикла (в часах).
        logger.info(f'Waiting for the next cycle. The waiting time: {GETTING_SCHEDULE_TIME_HOURS / 60 / 60} hours...\n')
        time.sleep(GETTING_SCHEDULE_TIME_HOURS)


# =====================================

if __name__ == '__main__':
    main()
