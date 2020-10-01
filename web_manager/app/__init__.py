from flask import Flask
import flask_admin as admin

from app.views import UserView, InstitutesView, AnalyticsView, IndexView

from app.storage import db

# Создаём приложение
app = Flask(__name__)

# ==========Настройки==========
# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# ==========URLs==========
app.add_url_rule('/', view_func=IndexView.as_view('index'))

# ==========Админ панель==========
admin = admin.Admin(app, name='Smart-schedule-IRNITU manager')

# Добавляем views
admin.add_view(UserView(db.users, 'Users', category='База данных'))
admin.add_view(AnalyticsView(name='Analytics', endpoint='analytics'))
admin.add_view(InstitutesView(db.institutes, 'Institutes', category='База данных'))
