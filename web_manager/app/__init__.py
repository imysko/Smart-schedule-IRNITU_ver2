from flask import Flask
import flask_admin as admin

from app.forms import UserView
from app.storage import db


# Create application
app = Flask(__name__)

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# Create admin
admin = admin.Admin(app, name='Smart-schedule-IRNITU manager')

# Add views
admin.add_view(UserView(db.users, 'Users'))