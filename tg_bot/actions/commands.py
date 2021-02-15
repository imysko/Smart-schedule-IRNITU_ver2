from tools import keyboards, statistics


def start(bot, message, storage, tz):
    """Команда бота Начать"""
    chat_id = message.chat.id

    # Проверяем есть пользователь в базе данных
    if storage.get_user(chat_id):
        storage.delete_user_or_userdata(chat_id)  # Удаляем пользвателя из базы данных

    bot.send_message(chat_id=chat_id, text='Привет!\n')
    bot.send_message(chat_id=chat_id, text='Для начала пройдите небольшую регистрацию😉\n'
                                           'Выберите институт',
                     reply_markup=keyboards.make_inline_keyboard_choose_institute(storage.get_institutes()))

    statistics.add(action='start', storage=storage, tz=tz)


def registration(bot, message, storage, tz):
    """Команда бота Регистрация"""
    chat_id = message.chat.id
    storage.delete_user_or_userdata(chat_id=chat_id)
    bot.send_message(chat_id=chat_id, text='Пройдите повторную регистрацию😉\n'
                                           'Выберите институт',
                     reply_markup=keyboards.make_inline_keyboard_choose_institute(storage.get_institutes()))

    statistics.add(action='reg', storage=storage, tz=tz)


def show_map(bot, message, storage, tz):
    """Команда бота Карта"""
    chat_id = message.chat.id
    bot.send_photo(chat_id, (open('map.jpg', "rb")))
    statistics.add(action='map', storage=storage, tz=tz)


def authors(bot, message, storage, tz):
    """Команда бота Авторы"""
    chat_id = message.chat.id
    bot.send_message(chat_id=chat_id, parse_mode='HTML',
                     text='<b>Авторы проекта:\n</b>'
                          '- Алексей @bolanebyla\n'
                          '- Султан @ace_sultan\n'
                          '- Александр @alexandrshen\n'
                          '- Владислав @TixoNNNAN\n'
                          '- Кирилл @ADAMYORT\n\n'
                          'По всем вопросом и предложениям пишите нам в личные сообщения. '
                          'Будем рады 😉\n'
                     )

    statistics.add(action='authors', storage=storage, tz=tz)


def help_info(bot, message, storage, tz):
    chat_id = message.chat.id
    bot.send_message(chat_id=chat_id, text='Список команд:\n'
                                           '/about - описание чат бота\n'
                                           '/authors - Список авторов \n'
                                           '/reg - повторная регистрация \n'
                                           '/map - карта университета \n')

    statistics.add(action='help', storage=storage, tz=tz)


def about(bot, message, storage, tz):
    chat_id = message.chat.id
    bot.send_message(chat_id=chat_id, parse_mode='HTML',
                     text='<b>О боте:\n</b>'
                          'Smart schedule IRNITU bot - это чат бот для просмотра расписания занятий в '
                          'Иркутском национальном исследовательском техническом университете\n\n'
                          '<b>Благодаря боту можно:\n</b>'
                          '- Узнать актуальное расписание\n'
                          '- Нажатием одной кнопки увидеть информацию о ближайшей паре\n'
                          '- Настроить гибкие уведомления с информацией из расписания, '
                          'которые будут приходить за определённое время до начала занятия')

    statistics.add(action='about', storage=storage, tz=tz)
