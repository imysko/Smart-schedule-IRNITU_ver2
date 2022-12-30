import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# MONGO_DB_ADDR = os.environ.get('MONGO_DB_ADDR')
# MONGO_DB_PORT = os.environ.get('MONGO_DB_PORT')
# MONGO_DB_PASSWORD = os.environ.get('MONGO_DB_PASSWORD')
# MONGO_DB_USER = os.environ.get('MONGO_DB_USER')
MONGO_URL = os.environ.get("MONGO_URL")
MONGO_DB_DATABASE = os.environ.get('MONGO_DB_DATABASE')


class MongodbService(object):
    _instance = None
    _client = None
    _db = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls.__init__(cls._instance)
        return cls._instance

    def __init__(self):
        self._client = MongoClient(MONGO_URL)
        self._db = self._client[MONGO_DB_DATABASE]

    def get_data(self, collection) -> list:
        return list(self._db[collection].find())

    def save_data(self, collection, data: dict):
        return self._db[collection].insert_one(data)


class MongodbServiceTG(MongodbService):
    def __init__(self):
        super().__init__()

    def get_users_with_reminders(self):
        return list(self._db.users.find(filter={'notifications': {'$ne': 0}}))

    def create_user(self, chat_id: int):
        update = {'chat_id': chat_id, 'institute': '', 'course': '', 'group': '', 'group_id': '', 'notifications': 0, 'reminders': []}
        self._db.users.update_one(filter={'chat_id': chat_id}, update={'$set': update}, upsert=True)

    def save_or_update_user(
            self,
            chat_id: int,
            *args,
            **kwargs,
    ):
        update = {'chat_id': chat_id, **kwargs}
        self._db.users.update_one(filter={'chat_id': chat_id}, update={'$set': update}, upsert=True)

    def get_user(self, chat_id: int):
        return self._db.users.find_one(filter={'chat_id': chat_id})

    def delete_user_or_userdata(self, chat_id: int, delete_only_course: bool = False):
        if delete_only_course:
            return self._db.users.update_one(filter={'chat_id': chat_id}, update={'$unset': {'course': ''}},
                                             upsert=True)
        return self._db.users.delete_one(filter={'chat_id': chat_id})


class MongodbServiceVK(MongodbService):
    def __init__(self):
        super().__init__()

    def get_users_with_reminders(self):
        return list(self._db.VK_users.find(filter={'notifications': {'$ne': 0}}))

    def create_user(self, chat_id: str):
        update = {'chat_id': chat_id, 'institute': '', 'course': '', 'group': '', 'group_id': '', 'notifications': 0, 'reminders': []}
        self._db.VK_users.update_one(filter={'chat_id': chat_id}, update={'$set': update}, upsert=True)

    def save_or_update_user(
            self,
            chat_id: int,
            institute=None,
            course=None,
            group=None,
            group_id=None,
            notifications=None,
            reminders=None
    ):
        update = {'chat_id': chat_id}
        if institute:
            update['institute'] = institute
        if course:
            update['course'] = course
        if group:
            update['group'] = group
        if group_id:
            update['group_id'] = group_id
        if notifications:
            update['notifications'] = notifications
        if reminders:
            update['reminders'] = reminders

        self._db.VK_users.update_one(filter={'chat_id': chat_id}, update={'$set': update}, upsert=True)
