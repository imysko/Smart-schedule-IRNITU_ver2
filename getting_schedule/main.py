from functions import postgre_storage
import data_conversion
from functions.mongo_storage import MongodbService

from pymongo.errors import PyMongoError
import psycopg2

import time
import os

# Задержка работы цикла (в часах).
GETTING_SCHEDULE_TIME_HOURS = float(os.environ.get('GETTING_SCHEDULE_TIME_HOURS')
                                    if os.environ.get('GETTING_SCHEDULE_TIME_HOURS')
                                    else 1) * 60 * 60

mongo_storage = MongodbService().get_instance()


def processing_institutes():
    """Обработка институтов"""
    print('Start processing_institutes...')
    start_time = time.time()

    try:
        # Получаем данные.
        pg_institutes = postgre_storage.get_institutes()
        # Преобразуем данные в нужный формат.
        mongo_institutes = sorted(data_conversion.convert_institutes(pg_institutes),
                                  key=lambda x: x['name'])  # Сортируем массив
        # Сохраняем данные.
        mongo_storage.save_institutes(mongo_institutes)

        end_time = time.time()
        print('Processing_institutes successful.', f'Operation time: {end_time - start_time} seconds.')

    except PyMongoError as e:
        print('Mongo error:\n', e)
    except psycopg2.OperationalError as e:
        print('Postgre error:\n', e)
    except Exception as e:
        print('convert_institutes error:\n', e)


def processing_groups_and_courses():
    """Обработка групп и курсов"""
    print('Start processing_groups...')
    start_time_groups = time.time()
    try:
        # Группы
        pg_groups = postgre_storage.get_groups()
        mongo_groups = sorted(data_conversion.convert_groups(pg_groups),
                              key=lambda x: x['name'])
        mongo_storage.save_groups(mongo_groups)  # Сохраняем группы

        end_time_groups = time.time()
        print('Processing_groups successful.', f'Operation time: {end_time_groups - start_time_groups} seconds.')
        print('Start processing_courses...')
        start_time_courses = time.time()

        try:
            # Курсы
            mongo_courses = sorted(data_conversion.convert_courses(mongo_groups),
                                   key=lambda x: x['name'])
            mongo_storage.save_courses(mongo_courses)  # Сохраняем курсы
        except PyMongoError as e:
            print('Mongo error:\n', e)
        except Exception as e:
            print('convert_courses error:')
            print(e)

        end_time_courses = time.time()
        print('Processing_courses successful.', f'Operation time: {end_time_courses - start_time_courses} seconds.')

    except PyMongoError as e:
        print('Mongo error:\n', e)
    except psycopg2.OperationalError as e:
        print('Postgre error:\n', e)
    except Exception as e:
        print('convert_groups error:\n', e)


def processing_teachers():
    """Обработка преподавателей"""
    print('Start processing_teachers...')
    start_time = time.time()

    try:
        pg_teachers = postgre_storage.get_teachers()
        mongo_teachers = sorted(data_conversion.convert_teachers(pg_teachers),
                                key=lambda x: x['prep'])  # Сортируем массив
        mongo_storage.save_teachers(mongo_teachers)

        end_time = time.time()
        print('Processing_teachers successful.', f'Operation time: {end_time - start_time} seconds.')

    except PyMongoError as e:
        print('Mongo error:\n', e)
    except psycopg2.OperationalError as e:
        print('Postgre error:\n', e)
    except Exception as e:
        print('convert_teachers error:\n', e)


def processing_schedule():
    """Обработка расписания"""
    print('Start processing_schedule...')
    start_time1 = time.time()

    pg_schedule = postgre_storage.get_schedule()

    # Расписание студентов
    try:
        mongo_schedule = data_conversion.convert_schedule(pg_schedule)

        if mongo_schedule:
            mongo_storage.save_schedule(mongo_schedule)
        else:
            mongo_storage.delete_schedule()

        end_time1 = time.time()
        print('Processing_schedule successful.', f'Operation time: {end_time1 - start_time1} seconds.')

    except PyMongoError as e:
        print('Mongo error:\n', e)
    except psycopg2.OperationalError as e:
        print('Postgre error:\n', e)
    except Exception as e:
        print('convert_schedule error:\n', e)

    # Расписание преподавателей
    print('Start processing_teachers_schedule...')
    start_time2 = time.time()
    try:
        mongo_teachers_schedule = data_conversion.convert_teachers_schedule(pg_schedule)

        if mongo_teachers_schedule:
            mongo_storage.save_teachers_schedule(mongo_teachers_schedule)
        else:
            mongo_storage.delete_teachers_schedule()

        end_time2 = time.time()
        print('Processing_teachers_schedule successful.', f'Operation time: {end_time2 - start_time2} seconds.')
    except PyMongoError as e:
        print('Mongo error:\n', e)
    except psycopg2.OperationalError as e:
        print('Postgre error:\n', e)
    except Exception as e:
        print('convert_teachers_schedule error:\n', e)

    # Расписание аудиторий
    print('Start processing_auditories_schedule...')
    start_time3 = time.time()
    try:
        mongo_auditories_schedule = data_conversion.convert_auditories_schedule(pg_schedule)

        if mongo_auditories_schedule:
            mongo_storage.save_auditories_schedule(mongo_auditories_schedule)
        else:
            mongo_storage.delete_auditories_schedule()

        end_time3 = time.time()
        print('Processing_auditories_schedule successful.', f'Operation time: {end_time3 - start_time3} seconds.')
    except PyMongoError as e:
        print('Mongo error:\n', e)
    except psycopg2.OperationalError as e:
        print('Postgre error:\n', e)
    except Exception as e:
        print('convert_auditories_schedule error:\n', e)

def main():
    while True:
        # Время начала работы цикла.
        start_time = time.time()

        # Институты
        processing_institutes()

        # Группы и курсы
        processing_groups_and_courses()

        # Преподаватели
        processing_teachers()

        # Расписание
        processing_schedule()

        # Время окончания работы цикла.
        end_time = time.time()
        print('Total operating time', f"--- {end_time - start_time} seconds ---")

        # Задержка работы цикла (в часах).
        print(f'Waiting for the next cycle. The waiting time: {GETTING_SCHEDULE_TIME_HOURS / 60 / 60} hours...\n')
        time.sleep(GETTING_SCHEDULE_TIME_HOURS)


# =====================================

if __name__ == '__main__':
    main()

    print(postgre_storage.get_schedule()[:1000])


