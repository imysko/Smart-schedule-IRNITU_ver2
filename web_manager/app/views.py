from flask_admin.contrib.pymongo import ModelView, filters
from flask.views import View
import flask_admin as admin
from flask_admin import BaseView, expose

from app.storage import db
from app.bots import tg_bot

from flask import redirect, url_for, request, flash
from app.forms import UserForm, InstitutesForm, CoursesForm, ScheduleForm, GroupsForm, BotSendMessageForm, StatisticForm


# Flask views
class IndexView(View):
    """отображение стартовой страницы"""

    def dispatch_request(self):
        return '<a href="/admin/">Click me to get to Admin!</a>'


# Create custom admin views
class AnalyticsView(BaseView):
    @expose('/', methods=['get'])
    def index(self):
        counts = {}
        cur=db.tg_statistics.find()
        actions = sorted(set([action['action'] for action in cur]))
        for _ in actions:
            name = db.tg_statistics.find({'action':_})
            count = name.count()
            counts[_]=count

        return self.render('admin/analytics_index.html', actions=actions,counts=counts)


class BotSendMessageView(BaseView):
    """Отправка сообщений всем пользователям tg бота"""

    @expose('/', methods=['get', 'post'])
    def index(self):
        form = BotSendMessageForm()
        # если нажали кнопку "Отправить"
        if request.method == 'POST':
            text = request.form.get('text')
            template = request.form.get('template')
            keyboard = request.form.get('keyboard')

            # Сотрим какой шаблон был выбран
            if template == 'Важное сообщение':
                text = '‼️Важное сообщение ‼️\n' + text
            elif template == 'Информационное сообщение':
                text = '⚠️Информационное сообщение⚠️\n' + text

            if keyboard == 'Основное меню':
                keyboard = tg_bot.make_keyboard_start_menu()
            else:
                keyboard = None

            # отправляем сообщения
            status, message, exceptions = tg_bot.send_message_to_all_users(text=text, keyboard=keyboard)

            if status and not exceptions:
                # Выводим сообщение об успехе
                flash(message, category='success')

            elif status and exceptions:
                # Выводим сообщение об успехе
                flash('Сообщения отправлены', category='success')
                # Выводим предупрежение
                flash(message, category='warning')

            else:
                # Выводим сообщение об ошибке
                flash(message, category='error')
                # не обновляем форму
                return self.render('admin/tg_bot/send_message.html', form=form)
            return redirect(url_for('tg_bot_send_messages.index'))

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
        groups = db.groups.find()
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


class ScheduleView(ModelView):
    column_list = ('group',)
    column_sortable_list = ('group',)
    form = ScheduleForm

    def _feed_group_choices(self, form):
        """формируем список групп для выбора"""
        groups = db.schedule.find()
        form.group.choices = [group['group'] for group in groups]
        return form

    def create_form(self):
        form = super(ScheduleView, self).create_form()
        return self._feed_group_choices(form)

    def edit_form(self, obj):
        """выводим группы когда редактируем"""
        form = super(ScheduleView, self).edit_form(obj)
        return self._feed_group_choices(form)


class InstitutesView(ModelView):
    column_list = ('name', 'link')  # что будет показываться на странице из формы (какие поля)
    column_sortable_list = ('name')  # что сортируется
    form = InstitutesForm

    def _feed_institutes_choices(self, form):
        """формируем список групп для выбора"""
        institutes = db.institutes.find()
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


class CoursesView(ModelView):
    column_list = ('institute', 'name')  # что будет показываться на странице из формы (какие поля)
    column_sortable_list = ('institute')  # что сортируется
    form_excluded_columns = ('name')
    form = CoursesForm

    def _feed_courses_choices(self, form):
        # form.name.choices = ['1 курс','2 курс', '3 курс']
        return form

    def create_form(self):
        form = super(CoursesView, self).create_form()
        return self._feed_courses_choices(form)

    def edit_form(self, obj):
        """выводим группы когда редактируем"""
        form = super(CoursesView, self).edit_form(obj)
        return self._feed_courses_choices(form)


class GroupsView(ModelView):
    column_list = ('name', 'course', 'link', 'institute')  # что будет показываться на странице из формы (какие поля)
    column_sortable_list = ('name')  # что сортируется
    form_excluded_columns = ('name')
    form = GroupsForm

    def _feed_group_choices(self, form):
        """формируем список групп для выбора"""
        groups = db.groups.find()
        form.name.choices = [group['name'] for group in groups]
        return form

    def create_form(self):
        form = super(GroupsView, self).create_form()
        return self._feed_group_choices(form)

    def edit_form(self, obj):
        """выводим группы когда редактируем"""
        form = super(GroupsView, self).edit_form(obj)
        return self._feed_group_choices(form)

class StatisticView(ModelView):
    column_list = ('action', 'date', 'time')  # что будет показываться на странице из формы (какие поля)
    column_sortable_list = ('action')  # что сортируется
    form_excluded_columns = ('date')
    form = StatisticForm

    def on_form_prefill(self, form, id):
        """делает поле chat_id неизменяемым"""
        form.action.render_kw = {'readonly': True}
        form.date.render_kw = {'readonly': True}
        form.time.render_kw = {'readonly': True}