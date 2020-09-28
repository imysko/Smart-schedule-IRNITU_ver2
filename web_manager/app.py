import pymongo

from flask import Flask
import flask_admin as admin

from wtforms import form, fields, validators

from flask_admin.form import Select2Widget
from flask_admin.contrib.pymongo import ModelView, filters
from flask_admin.model.fields import InlineFormField, InlineFieldList, FieldList


# Create application
app = Flask(__name__)

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# Create models
conn = pymongo.Connection()
db = conn.Smart_schedule_IRNITU  # Наша база данных


# TG User admin
class InnerFormDays(form.Form):
    """списки со временем напоминаний"""
    понедельник = InlineFieldList(fields.StringField(), 'понедельник')
    вторник = InlineFieldList(fields.StringField(), 'вторник')
    среда = InlineFieldList(fields.StringField(), 'среда')
    четверг = InlineFieldList(fields.StringField(), 'четверг')
    пятница = InlineFieldList(fields.StringField(), 'пятница')
    суббота = InlineFieldList(fields.StringField(), 'суббота')


class InnerFormWeeks(form.Form):
    even = InlineFormField(InnerFormDays, 'Четная неделя')
    odd = InlineFormField(InnerFormDays, 'Нечетная неделя')


class UserForm(form.Form):
    """создаём форму"""
    chat_id = fields.StringField('chat_id', [validators.DataRequired()])  # поле с chat_id в базе
    group = fields.SelectField('Группа', widget=Select2Widget())  # поле с group в базе
    notifications = fields.IntegerField('За сколько минут делать напоминания', default=0)  # поле с chat_id в базе

    reminders = InlineFormField(InnerFormWeeks, 'Время напоминаний', default={})  # поле с reminders в базе


class UserView(ModelView):
    """создаём отображение формы"""

    column_list = ('chat_id', 'group', 'notifications')  # что будет показываться на странице из формы (какие поля)
    column_sortable_list = ('chat_id', 'group', 'notifications')  # что сортируется

    def on_form_prefill(self, form, id):
        """делает поле chat_id неизменяемым"""
        form.chat_id.render_kw = {'readonly': True}

    form = UserForm

    def _feed_group_choices(self, form):
        """формируем список групп для выбора"""
        groups = db.groups.find(fields=('name',))
        form.group.choices = [group['name'] for group in groups]
        return form

    def create_form(self):
        """выводим группы когда создаём"""
        form = super(UserView, self).create_form()
        return self._feed_group_choices(form)

    def edit_form(self, obj):
        """выводим группы когда редактируем"""
        form = super(UserView, self).edit_form(obj)
        return self._feed_group_choices(form)


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
