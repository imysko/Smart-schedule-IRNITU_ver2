from flask_admin.contrib.pymongo import ModelView, filters
from flask.views import View
import flask_admin as admin
from flask_admin import BaseView, expose

from app.storage import db
from app.forms import UserForm, InstitutesForm, BotSendMessageForm


from flask import redirect,  url_for, request, flash

# Flask views
class IndexView(View):
    """отображение стартовой страницы"""

    def dispatch_request(self):
        return '<a href="/admin/">Click me to get to Admin!</a>'


# Create custom admin views
class AnalyticsView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/analytics_index.html')


class BotSendMessageView(BaseView):
    """Отправка сообщений всем пользователям tg бота"""
    @expose('/', methods=['get', 'post'])
    def index(self):
        form = BotSendMessageForm()
        # если нажали кнопку "Отправить"
        if request.method == 'POST':
            sent_message = True # Если сообщение было отправлено, то True
            if sent_message:
                # Выводим сообщение об успехе
                flash('Сообщение отправлено', category='success')
            else:
                # Выводим сообщение об ошибке
                flash('Сообщение не отправлено', category='error')
            return redirect(url_for('tg_bot.index'))

        return self.render('admin/tg_bot/send_message.html', form=form)


# Create Model Views
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


class InstitutesView(ModelView):
    column_list = ('name', 'link')  # что будет показываться на странице из формы (какие поля)
    column_sortable_list = ('name')  # что сортируется
    form = InstitutesForm

    def _feed_institutes_choices(self, form):
        """формируем список групп для выбора"""
        institutes = db.institutes.find(fields=('name',))
        form.name.choices = [institute['name'] for institute in institutes]
        return form

    def create_form(self):
        """выводим группы когда создаём"""
        form = super(InstitutesView, self).create_form()
        return self._feed_institutes_choices(form)

    def edit_form(self, obj):
        """выводим группы когда редактируем"""
        form = super(InstitutesView, self).edit_form(obj)
        return self._feed_institutes_choices(form)
