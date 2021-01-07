import os
from pymongo import MongoClient

MONGO_DB_ADDR = os.environ.get('MONGO_DB_ADDR', default='localhost')
MONGO_DB_PORT = os.environ.get('MONGO_DB_PORT', default=27017)
MONGO_DB_DATABASE = os.environ.get('MONGO_DB_DATABASE', default='Smart_schedule_IRNITU')


class MongodbService(object):
    _instance = None
    _client = None
    _db = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls.__init__(cls._instance, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self._client = MongoClient(f'mongodb://{MONGO_DB_ADDR}:{MONGO_DB_PORT}')
        self._db = self._client[MONGO_DB_DATABASE]

    def save_institutes(self, institutes: list):
        """Сохраняет список институтов в коллекцию institutes"""
        self._db.institutes.drop()  # очищаем старые записи в коллекции
        return self._db.institutes.insert_many(institutes)

    def save_courses(self, courses: list):
        """Сохраняет список курсов в коллекцию courses"""
        self._db.courses.drop()  # очищаем старые записи в коллекции
        return self._db.courses.insert_many(courses)

    def save_groups(self, groups: list):
        """Сохраняет список групп в коллекцию groups"""
        self._db.groups.drop()  # очищаем старые записи в коллекции
        return self._db.groups.insert_many(groups)

    def save_schedule(self, schedule: dict):
        """Сохраняет расписание в коллекцию schedule"""
        return self._db.schedule.update_one(filter={'group': schedule['group']}, update={'$set': schedule}, upsert=True)

    def save_status(self, date, time, getting_schedule_time_hours):
        """Сохраняет время последнего обращения к PostgreSQL"""
        status = {
            'name': 'getting_schedule',
            'date': date,
            'time': time,
            'getting_schedule_time_hours': getting_schedule_time_hours
        }

        return self._db.status.update_one(filter={'name': 'getting_schedule'}, update={'$set': status}, upsert=True)
