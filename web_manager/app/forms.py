from wtforms import form, fields, validators

from flask_admin.form import Select2Widget

from flask_admin.model.fields import InlineFormField, InlineFieldList, FieldList



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
    chat_id = fields.IntegerField('chat_id', [validators.DataRequired()])  # поле с chat_id в базе
    group = fields.SelectField('Группа', widget=Select2Widget())  # поле с group в базе
    notifications = fields.IntegerField('За сколько минут делать напоминания', default=0)  # поле с chat_id в базе

    reminders = InlineFormField(InnerFormWeeks, 'Время напоминаний', default={})  # поле с reminders в базе


