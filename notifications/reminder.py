import locale
import platform
import threading
from datetime import datetime, timedelta
from typing import Literal

import pytz

from db.getting_schedule import get_group_schedule
from db.mongo_storage import MongodbServiceTG, MongodbServiceVK
from tools.schedule_tools.notifications import check_that_user_has_reminder_enabled_for_the_current_time, \
    forming_user_to_submit, check_that_the_lesson_has_the_right_time, convert_minutes_word
from tools.schedule_tools.schedule_conversion import convert_lessons_reminder
from tools.logger import logger

TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk')
locale_name = ('ru_RU.UTF-8' if platform.system() == 'Linux' else 'ru_RU')
locale.setlocale(locale.LC_TIME, locale_name)


class Reminder:
    def __init__(self, bot_platform: Literal['vk', 'tg'], bot):
        self.platform = bot_platform
        self.__check_platform()
        self.bot = bot
        self.storage = MongodbServiceTG() if bot_platform == 'tg' else MongodbServiceVK()
        self.users = []

    def sending_notifications(self):
        print('here')
        for user in self.users:
            chat_id = user['chat_id']
            time = user['time']
            group = user['group']
            notifications = user['notifications']

            try:
                day = get_group_schedule(group_id=group, selected_date=datetime.now(TZ_IRKUTSK) + timedelta(days=3))
            except Exception as e:
                logger.exception(f'Error (group: {group}):\n{e}')
                return

            if not day:
                continue

            print(day)
            for lesson in day[0]['lessons']:
                print(lesson)
                if not check_that_the_lesson_has_the_right_time(time, lesson['lesson_start']):
                    day.remove(lesson)

            lessons_for_reminders = convert_lessons_reminder(lessons=day[0]['lessons'])

            if not lessons_for_reminders:
                continue

            text = f'Через {notifications} {convert_minutes_word(notifications)} пара\n' \
                   f'{lessons_for_reminders}'

            if self.platform == 'tg':
                try:
                    self.bot.send_message(chat_id=chat_id, text=text)
                except Exception as e:
                    logger.exception(f'---TG---\n{e}')
            elif self.platform == 'vk':
                try:
                    logger.info(f'vk send user_id: {chat_id}')
                    self.bot.method('messages.send', {'user_id': chat_id, 'message': text, 'random_id': 0})
                except Exception as e:
                    logger.exception(f'---VK---\n{e}')

    def __check_platform(self):
        if self.platform == 'vk':
            logger.info('reminders_vk is started')
        elif self.platform == 'tg':
            logger.info('reminders_tg is started')
        else:
            raise ValueError(f'Нет такой платформы: {self.platform}')

    def search_for_reminders(self):
        logger.info(f'{self.platform} сработало')
        time_now = datetime.now(TZ_IRKUTSK)
        day_now = datetime.now(TZ_IRKUTSK).strftime('%A').lower()

        threading.Timer(60, self.search_for_reminders).start()

        self.users = []

        reminders = self.storage.get_users_with_reminders()

        for reminder in reminders:
            if 'reminders' not in reminder.keys():
                continue

            user_days = reminder['reminders']

            if not user_days:
                continue

            user_day_reminder_time = user_days.get(day_now.lower())

            if check_that_user_has_reminder_enabled_for_the_current_time(time_now, user_day_reminder_time):
                chat_id = reminder['chat_id']
                group = reminder['group']
                notifications = reminder['notifications']

                user = forming_user_to_submit(chat_id, group, notifications, day_now, time_now)
                self.users.append(user)

        self.sending_notifications()
