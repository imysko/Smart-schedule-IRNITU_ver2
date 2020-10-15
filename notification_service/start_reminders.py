"""Запуск напоминаний от вк и tg в двух потокках"""

from threading import Thread
import reminders_tg
import reminders_vk

tg = Thread(target=reminders_tg.search_for_reminders)
vk = Thread(target=reminders_vk.search_for_reminders)

tg.start()
vk.start()
