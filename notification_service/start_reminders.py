"""Запуск напоминаний от вк и tg в двух потоках"""
import json
import os
from threading import Thread
from time import sleep

import telebot
import vk_api
from dotenv import load_dotenv
from telebot.apihelper import ApiTelegramException

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

    test = True

    with open("sent.txt", "a") as f:
        for i in data:
            if not test:
                chat_id = str(i['chat_id'])
                if chat_id in sent_chats:
                    continue
            else:
                chat_id = 1112043053

            print(chat_id)
            f.write(f"{chat_id}\n")
            f.flush()

            try:
                tg_bot.send_message(chat_id, """В связи с возвращением части преподавателей из дистанционки, со следующей недели обновляется расписание. Будьте внимательны.""".strip())

                # tg_bot.send_photo(
                #     chat_id,
                #     open("C:\_SRP\_soft\Smart-schedule-IRNITU2\d95b17f8-ceab-4eae-8153-2fbd25118024.jpg", 'rb'),
                #     caption="🕺🕺🕺 минутка рекламы 💃💃💃",
                # )
            except ApiTelegramException as ex:
                print(str(ex))

            if test:
                break

if __name__ == '__main__':
    main()
