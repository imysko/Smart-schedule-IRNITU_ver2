import pymongo
from bson.objectid import ObjectId

from flask import Flask
import flask_admin as admin

from wtforms import form, fields

from flask_admin.form import Select2Widget
from flask_admin.contrib.pymongo import ModelView, filters
from flask_admin.model.fields import InlineFormField, InlineFieldList

# Create application
app = Flask(__name__)

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# Create models
conn = pymongo.Connection()
db = conn.Smart_schedule_IRNITU  # Наша база данных


# TG User admin
class UserForm(form.Form):
    """создаём форму"""
    chat_id = fields.StringField('chat_id')  # поле с chat_id в базе
    group = fields.StringField('group')  # поле с group в базе
    reminders = fields.StringField('reminders')  # поле с reminders в базе


class UserView(ModelView):
    """создаём отображение формы"""

    column_list = ('chat_id', 'group', 'reminders')  # что будет показываться на странице из формы (какие поля)
    column_sortable_list = ('chat_id', 'group', 'reminders')  # что сортируется

    form = UserForm


# Flask views
@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'


if __name__ == '__main__':
    # Create admin
    admin = admin.Admin(app, name='Example: PyMongo')

    # Add views
    admin.add_view(UserView(db.users, 'Users'))

    # Start app
    app.run(debug=True)
