import time

from tools.logger import logger
from db.getting_schedule import get_group_schedule
from db.mongo_storage import MongodbServiceTG, MongodbServiceVK
from tools.schedule_tools.notifications import calculating_reminder_times


class ReminderUpdater:
    def __init__(self):
        self.users = []

    def start(self):
        self.print_status_info()
        while True:
            self.calculation()
            time.sleep(1 * 60 * 60)

    def get_users(self) -> list:
        raise NotImplementedError

    def save_user(self, user: dict):
        raise NotImplementedError

    def calculation(self):
        self.users = self.get_users()

        for user in self.users:
            group = user['group_id']
            if not group:
                continue

            schedule = get_group_schedule(group)
            if not schedule:
                continue

            try:
                reminders = calculating_reminder_times(schedule=schedule, time=int(user['notifications']))
            except Exception as e:
                logger.error(e)
                continue
            user['reminders'] = reminders
            self.save_user(user)

    @staticmethod
    def print_status_info():
        raise NotImplementedError


class TGReminderUpdater(ReminderUpdater):
    def __init__(self):
        super().__init__()
        self.storage = MongodbServiceTG()

    def get_users(self):
        return self.storage.get_users_with_reminders()

    def save_user(self, user: dict):
        del user['_id']
        self.storage.save_or_update_user(**user)

    @staticmethod
    def print_status_info():
        logger.info('tg_reminder_updater is started')


class VKReminderUpdater(ReminderUpdater):
    def __init__(self):
        super().__init__()
        self.storage = MongodbServiceVK()

    def get_users(self):
        return self.storage.get_users_with_reminders()

    def save_user(self, user: dict):
        del user['_id']
        self.storage.save_or_update_user(**user)

    @staticmethod
    def print_status_info():
        logger.info('vk_reminder_updater is started')
