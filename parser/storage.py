import os
from pymongo import MongoClient

MONGO_DB_ADDR = os.environ.get('MONGO_DB_ADDR')
MONGO_DB_PORT = os.environ.get('MONGO_DB_PORT')
MONGO_DB_DATABASE = os.environ.get('MONGO_DB_DATABASE')


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

    def get_data(self, collection) -> list:
        """возвращает список документов из указанной коллекции"""
        return list(self._db[collection].find())

    def save_institutes(self, institutes: list):
        """сохраняет список институтов в коллекцию institutes"""
        self._db.institutes.drop() # очищаем старые записи в коллекции
        return self._db.institutes.insert_many(institutes)

    def save_courses(self, courses: list):
        """сохраняет список курсов в коллекцию courses"""
        return self._db.courses.insert_many(courses)

    def save_groups(self, groups: list):
        """сохраняет список групп в коллекцию groups"""
        return self._db.groups.insert_many(groups)

    def get_institutes(self) -> list:
        """возвращает список институтов"""
        return list(self._db.institutes.find())

    def get_courses(self, institute='') -> list:
        """возвращает список курсов у определённого института"""
        return list(self._db.courses.find(filter={'institute': {'$regex': f'{institute}*'}}))

    def get_groups(self, institute: str, course: str) -> list:
        """возвращает список групп на определённом курсе в определеннои институте"""
        return list(self._db.groups.find(filter={'institute': institute, 'course': course}))

    def save_schedule(self, schedule: dict):
        return self._db.schedule.insert_one(schedule)

    def get_schedule(self, group):
        """возвращает расписание группы"""
        return self._db.schedule.find_one(filter={'group': group})
