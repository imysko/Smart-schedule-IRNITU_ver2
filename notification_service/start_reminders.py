"""Запуск напоминаний от вк и tg в двух потокках"""

from threading import Thread
import notification_service
import reminders_vk

tg = Thread(target=notification_service.search_for_reminders)
vk = Thread(target=reminders_vk.search_for_reminders)

tg.start()
vk.start()
