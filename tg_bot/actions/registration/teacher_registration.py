import json
from tools import keyboards

prep_reg = {}


def start_prep_reg(bot, message, storage):
    """Вхождение в стейт регистрации преподавателей"""

    chat_id = message.message.chat.id
    message_id = message.message.message_id
    data = message.data

    # После того как пользователь выбрал институт
    if 'institute' in data:
        data = json.loads(data)

        storage.save_or_update_user(chat_id=chat_id,
                                    institute=data['institute'],
                                    course='None')  # Записываем в базу институт пользователя

        # Выводим сообщение со списком курсов
        bot.send_message(chat_id, text='📚Кто постигает новое, лелея старое,\n'
                                       'Тот может быть учителем.\n'
                                       'Конфуций')

        msg = bot.send_message(chat_id, text='Введите своё ФИО полностью.\n'
                                             'Например: Корняков Михаил Викторович')
        bot.register_next_step_handler(msg, reg_prep_step_2, bot, storage)
        bot.delete_message(message_id=message_id, chat_id=chat_id)

        return


def reg_prep_step_2(message, bot, storage, last_msg=None):
    """Регистрация преподавателя"""

    chat_id = message.chat.id
    message = message.text
    user = storage.get_user(chat_id)

    if not user:
        return

    if last_msg:
        message_id = last_msg.message_id
        bot.delete_message(message_id=message_id, chat_id=chat_id)

    prep_list = storage.get_prep(message)
    if prep_list:
        prep_name = prep_list[0]['prep']
        storage.save_or_update_user(chat_id=chat_id, group=prep_name)
        bot.send_message(chat_id, text=f'Вы успешно зарегистрировались, как {prep_name}!😊\n\n'
                                       'Для того чтобы пройти регистрацию повторно, напишите сообщение "Регистрация"\n',
                         reply_markup=keyboards.make_keyboard_start_menu())
        return

    elif not prep_list:
        # Делим введенное фио на части и ищем по каждой в базе
        prep_list = []
        prep_list_2 = []
        # Делим полученное ФИО на отдельные слова, на выходе имеем второй список с уникальными значениями по запросу
        for name_unit in message.split():
            # Ищем в базе преподов по каждому слову
            for i in storage.get_register_list_prep(name_unit):
                prep_list.append(i)
            # Если 2 списка не пустых, ищем элементы, которые повторяются максимальное количество раз
            if prep_list and prep_list_2:
                prep_list_2 = list(set(prep_list) & set(prep_list_2))
            # Если второй список пуст (еще остались слова из запроса, по которым не сходили в базу)
            elif prep_list and not prep_list_2:
                prep_list_2 = prep_list
            prep_list = []
        msg = bot.send_message(chat_id=chat_id, text=f'Возможно вы имелли в виду:',
                               reply_markup=keyboards.make_inline_keyboard_reg_prep(prep_list_2))
        bot.register_next_step_handler(msg, reg_prep_step_2, bot, storage, last_msg=msg)
    return


def reg_prep_choose_from_list(bot, message, storage):
    """Обрабатываем колбэк преподавателя"""

    chat_id = message.message.chat.id
    message_id = message.message.message_id
    data = json.loads(message.data)

    # Выходим из цикла поиска преподавателя по ФИО
    bot.clear_step_handler_by_chat_id(chat_id=chat_id)

    # Назад к институтам
    if data['prep_id'] == 'back':
        bot.send_message(chat_id=chat_id, text='Выберите институт',
                         reply_markup=keyboards.make_inline_keyboard_choose_institute(storage.get_institutes()))
        storage.delete_user_or_userdata(chat_id)
    # Регистрируем преподавателя по выбранной кнопке
    else:
        prep_name = storage.get_prep_for_id(data['prep_id'])['prep']
        storage.save_or_update_user(chat_id=chat_id, group=prep_name)
        bot.delete_message(message_id=message_id, chat_id=chat_id)
        bot.send_message(chat_id, text=f'Вы успешно зарегистрировались, как {prep_name}!😊\n\n'
                                       'Для того чтобы пройти регистрацию повторно, напишите сообщение "Регистрация"\n',
                         reply_markup=keyboards.make_keyboard_start_menu())
