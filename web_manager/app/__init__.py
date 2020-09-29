from flask import Flask
import flask_admin as admin

from app.views import UserView
from app.storage import db
from app import views

# Создаём приложение
app = Flask(__name__)

# ==========Настройки==========
# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# ==========URLs==========
app.add_url_rule('/', view_func=views.IndexView.as_view('index'))

# ==========Админ панель==========
admin = admin.Admin(app, name='Smart-schedule-IRNITU manager')

# Добавляем views
admin.add_view(UserView(db.users, 'Users'))
