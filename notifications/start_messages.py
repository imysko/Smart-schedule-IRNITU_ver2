from threading import Thread

from notifications.reminder import Reminder
from notifications.reminder_updater import TGReminderUpdater


def start_tg(tg_bot):
    tg_reminder = Reminder(bot_platform='tg', bot=tg_bot)
    reminder_updater_tg = TGReminderUpdater()

    tg = Thread(target=tg_reminder.search_for_reminders)
    tg_updater = Thread(target=reminder_updater_tg.start)

    tg.start()
    tg_updater.start()
