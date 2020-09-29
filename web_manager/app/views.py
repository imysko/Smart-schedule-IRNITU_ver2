from flask_admin.contrib.pymongo import ModelView, filters
from flask.views import View

from app.storage import db
from app.forms import UserForm

# Flask views
class IndexView(View):

    def dispatch_request(self):
        return '<a href="/admin/">Click me to get to Admin!</a>'


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