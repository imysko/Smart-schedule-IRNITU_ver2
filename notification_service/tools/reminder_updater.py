import time

from API.functions_api import calculating_reminder_times
from tools.logger import logger


class ReminderUpdater:

    def __init__(self, storage):
        self.users = []
        self.last_schedule_update_date = None
        self.storage = storage

    def start(self):
        self.print_status_info()
        while True:
            if self.check_updates_db():
                self.calculation()
            time.sleep(10 * 60)

    def get_users(self) -> list:
        raise NotImplementedError

    def save_user(self, user: dict):
        raise NotImplementedError

    def calculation(self):
        self.users = self.get_users()
        for user in self.users:

            group = user['group']

            schedule = self.storage.get_schedule(group=group)['schedule']

            try:
                reminders = calculating_reminder_times(schedule=schedule, time=int(user['notifications']))
            except Exception as e:
                logger.error(e)
                continue

            user['reminders'] = reminders
            self.save_user(user)

    def check_updates_db(self) -> bool:
        return True

    @staticmethod
    def print_status_info():
        raise NotImplementedError


class VKReminderUpdater(ReminderUpdater):

    def get_users(self):
        return self.storage.get_users_with_reminders_vk()

    def save_user(self, user: dict):
        del user['_id']
        self.storage.save_or_update_vk_user(**user)

    @staticmethod
    def print_status_info():
        logger.info('vk_reminder_updater is started')
