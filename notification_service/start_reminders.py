"""Запуск напоминаний от вк и tg в двух потоках"""
import json
import os
from threading import Thread
from time import sleep

import telebot
import vk_api
from dotenv import load_dotenv

from reminder import Reminder
from tools.reminder_updater import VKReminderUpdater, TGReminderUpdater

load_dotenv()

TG_TOKEN = os.environ.get('TG_TOKEN')
VK_TOKEN = os.environ.get('VK_TOKEN')

tg_bot = telebot.TeleBot(TG_TOKEN)
# tg_reminder = Reminder(bot_platform='tg', bot=tg_bot)

# vk_bot = vk_api.VkApi(token=VK_TOKEN)
# vk_reminder = Reminder(bot_platform='vk', bot=vk_bot)

# reminder_updater_vk = VKReminderUpdater()
# reminder_updater_tg = TGReminderUpdater()


def main():
    with open(r"C:\_SRP\_soft\Smart-schedule-IRNITU2\users.json", 'r') as f:
        data = json.load(f)

    sent_chats = []
    try:
        with open("sent.txt", "r") as f:
            sent_chats = [i.strip() for i in f.readlines()]
    except:
        pass

    with open("sent.txt", "a") as f:
        for i in data:
            chat_id = str(i['chat_id'])
            if chat_id in sent_chats:
                continue
            print(chat_id)
            f.write(f"{chat_id}\n")
            f.flush()

            tg_bot.send_message(chat_id, """
Умное расписание на связи, привет! 🤗

👉 мы исправили проблему с отображением расписания, и теперь оно снова актуальное
👉 также добавили поддержку проектного расписания для 3-го курса
✨ сейчас работаем с политехом, чтобы добавить возможность делать рассылки важных сообщений прямо через бот

А пока в тестовых целях и на правах рекламы 🙈
                """.strip())

            tg_bot.send_photo(
                chat_id,
                open("C:\_SRP\_soft\Smart-schedule-IRNITU2\d95b17f8-ceab-4eae-8153-2fbd25118024.jpg", 'rb'),
                caption="🕺🕺🕺 минутка рекламы 💃💃💃",
            )
            sleep(0.5)

if __name__ == '__main__':
    main()
