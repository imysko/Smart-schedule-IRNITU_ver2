import json
import os
from threading import Thread
from time import sleep

import telebot
import vk_api
from dotenv import load_dotenv
from telebot.apihelper import ApiTelegramException

from reminder import Reminder
from notifications.reminder_updater import VKReminderUpdater, TGReminderUpdater

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

    test = False

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
                tg_bot.send_message(chat_id,
                                    # open("C:\_SRP\_soft\Smart-schedule-IRNITU2\itacademy220126.jpg", 'rb'),
                                    """
  ИРНИТУ и En+ Group реализуют уникальный образовательный проект [Академия IT](http://itenergy.academy/), благодаря которому будущие специалисты в сфере Digital получат не только практические знания, но и высокооплачиваемую и интересную работу в известной компании. 
  Чтобы сделать учебный процесс более эффективным, нам важно знать ваше мнение по нижеприведенным вопросам.  Просим вас заполнить небольшую анкету [https://docs.google.com/forms/d/e/1FAIpQLSdQeGlxb5-BE1_nUZvaEAMT-YHQ5adVwULIV3Qc8SM3-E1mdQ/viewform?vc=0&c=0&w=1&flr=0](https://docs.google.com/forms/d/e/1FAIpQLSdQeGlxb5-BE1_nUZvaEAMT-YHQ5adVwULIV3Qc8SM3-E1mdQ/viewform?vc=0&c=0&w=1&flr=0)
  
  Полученные ответы помогут выявить и оценить сильные и слабые стороны проекта, а также максимально адаптировать его с учетом ваших запросов и ожиданий.  
                                  """.strip(), parse_mode="Markdown")
                # tg_bot.send_photo(
                #     chat_id,
                #     open(r"C:\_SRP\_soft\Smart-schedule-IRNITU2\vac122021_1.jpg", 'rb'),
                # )
                # tg_bot.send_photo(
                #     chat_id,
                #     open(r"C:\_SRP\_soft\Smart-schedule-IRNITU2\vac122021_2.jpg", 'rb'),
                #     caption="ИРНИТУ - COVID-19. Важное - https://www.istu.edu/deyatelnost/bezopasnost/covid/"
                # )
            except ApiTelegramException as ex:
                print(str(ex))

            if test:
                break


if __name__ == '__main__':
    main()