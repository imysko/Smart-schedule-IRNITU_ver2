from flask import Flask
import flask_admin as admin

from app.views import UserView, InstitutesView, AnalyticsView, StatisticView, IndexView, CoursesView, GroupsView, BotSendMessageView, \
    ScheduleView, ParserStatusView, VkUserView
from app.storage import db

# Создаём приложение
app = Flask(__name__,
            static_folder='static', )

# ==========Настройки==========
# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# ==========URLs==========
app.add_url_rule('/', view_func=IndexView.as_view('index'))
app.add_url_rule('/status/parser', view_func=ParserStatusView.as_view('parser_status'))

# ==========Админ панель==========
admin = admin.Admin(app, name='Умное расписание ИРНИТУ ', template_mode='bootstrap3')

# Добавляем views
admin.add_view(UserView(db.users, 'Пользователи Telegram', category='База данных'))
admin.add_view(VkUserView(db.VK_users, 'Пользователи Vk', category='База данных'))


admin.add_view(InstitutesView(db.institutes, 'Институты', category='База данных'))

admin.add_view(AnalyticsView(name='Аналитика', endpoint='analytics'))
admin.add_view(StatisticView(db.tg_statistics, 'Статистика Telegram', endpoint='statistics',category='База данных'))
admin.add_view(BotSendMessageView(name='Отправка сообщений',
                                  endpoint='tg_bot_send_messages', category='Телеграм бот'))

admin.add_view(CoursesView(db.courses, 'Курсы', category='База данных'))
admin.add_view(GroupsView(db.groups, 'Группы', category='База данных'))
admin.add_view(ScheduleView(db.schedule, 'Расписание', category='База данных'))

