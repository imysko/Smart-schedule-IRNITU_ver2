import json

from tools.tg_tools import keyboards
from tools import logger


def start_student_reg(bot, message, storage):
    chat_id = message.message.chat.id
    message_id = message.message.message_id
    data = message.data

    # После того как пользователь выбрал институт
    if 'institute' in data:
        data = json.loads(data)
        courses = storage.get_courses(data['institute'])

        storage.save_or_update_user(chat_id=chat_id,
                                    institute=data['institute'])  # Записываем в базу институт пользователя
        try:
            # Выводим сообщение со списком курсов
            bot.edit_message_text(message_id=message_id, chat_id=chat_id, text=f'Выберите курс',
                                  reply_markup=keyboards.make_inline_keyboard_choose_courses(courses))
        except Exception as e:
            logger.exception(e)
            return

    # После того как пользователь выбрал курс или нажал кнопку назад при выборе курса
    elif 'course' in data:
        data = json.loads(data)

        # Если нажали кнопку назад
        if data['course'] == 'back':
            storage.delete_user_or_userdata(
                chat_id=chat_id)  # Удаляем информацию об институте пользователя из базы данных
            try:
                bot.edit_message_text(message_id=message_id, chat_id=chat_id,
                                      text='Выберите институт',
                                      reply_markup=keyboards.make_inline_keyboard_choose_institute(
                                          storage.get_institutes()))
                return
            except Exception as e:
                logger.exception(e)
                return

        storage.save_or_update_user(chat_id=chat_id, course=data['course'])  # Записываем в базу курс пользователя
        user = storage.get_user(chat_id=chat_id)

        try:
            institute = user['institute']
            course = user['course']
            groups = storage.get_groups(institute=institute, course=course)
            # Выводим сообщение со списком групп
            bot.edit_message_text(message_id=message_id, chat_id=chat_id,
                                  text=f'Выберите группу',
                                  reply_markup=keyboards.make_inline_keyboard_choose_groups(groups))
        except Exception as e:
            logger.exception(e)
            return

    # После того как пользователь выбрал группу или нажал кнопку назад при выборе группы
    elif 'group' in data:
        data = json.loads(data)

        # Если нажали кнопку назад
        if data['group'] == 'back':
            # Удаляем информацию о курсе пользователя из базы данных
            storage.delete_user_or_userdata(chat_id=chat_id,
                                            delete_only_course=True)
            try:
                institute = storage.get_user(chat_id=chat_id)['institute']
            except Exception as e:
                logger.exception(e)
                return
            courses = storage.get_courses(institute=institute)

            try:
                # Выводим сообщение со списком курсов
                bot.edit_message_text(message_id=message_id, chat_id=chat_id, text=f'Выберите курс',
                                      reply_markup=keyboards.make_inline_keyboard_choose_courses(courses))
                return
            except Exception as e:
                logger.exception(e)
                return

        storage.save_or_update_user(chat_id=chat_id, group=data['group'])  # Записываем в базу группу пользователя

        try:
            # Удаляем меню регистрации
            bot.delete_message(message_id=message_id, chat_id=chat_id)
        except Exception as e:
            logger.exception(e)
            return

        bot.send_message(chat_id=chat_id,
                         text="Приветствую Вас, Пользователь! Вы успешно зарегистрировались!😊 \n\n"
                             "Я чат-бот для просмотра расписания занятий в Иркутском Политехе.🤖\n\n"
                             "С помощью меня можно не только смотреть свое расписание на день или неделю, но и осуществлять поиск расписания по группам, аудиториям и преподавателям (кнопка [Поиск]).\n"
                             "А еще можно настроить уведомления о парах (в разделе [Другое] кнопка [Напоминания]).\n\n"
                             "Следующие советы помогут раскрыть мой функционал на 💯 процентов:\n"
                             "⏭Используйте кнопки, так я буду Вас лучше понимать!\n\n"
                             "🌄Подгружайте расписание утром и оно будет в нашем чате до скончания времен!\n\n"
                             "📃Чтобы просмотреть список доступных команд и кнопок, напишите в чате [Помощь]\n\n"
                             "🆘Чтобы вызвать эту подсказку снова, напиши в чат [Подсказка] \n\n"
                             "Надеюсь, что Вам будет удобно меня использовать. Для того чтобы пройти регистрацию повторно, напишите сообщение [Регистрация]\n\n"
                             "Если Вы столкнетесь с технической проблемой, то Вы можете:\n"
                             "- обратиться за помощью в официальную группу ВКонтакте [https://vk.com/smartschedule]\n"
                             "- написать одному из моих создателей (команда Авторы)🤭\n",
                         reply_markup=keyboards.make_keyboard_start_menu())
