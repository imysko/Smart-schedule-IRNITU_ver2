import os
from threading import Thread

from telebot import TeleBot

from notifications.reminder import Reminder
from notifications.reminder_updater import TGReminderUpdater

TG_TOKEN = os.environ.get('TG_TOKEN')
VK_TOKEN = os.environ.get('VK_TOKEN')

tg_bot = TeleBot(TG_TOKEN)
tg_reminder = Reminder(bot_platform='tg', bot=tg_bot)
reminder_updater_tg = TGReminderUpdater()


def main():
    tg = Thread(target=tg_reminder.search_for_reminders)
    tg_updater = Thread(target=reminder_updater_tg.start)

    tg.start()
    tg_updater.start()


if __name__ == '__main__':
    main()
