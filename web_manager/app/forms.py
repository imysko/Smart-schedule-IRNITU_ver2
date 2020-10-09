from wtforms import form, fields, validators, SubmitField

from flask_admin.form import Select2Widget

from flask_admin.model.fields import InlineFormField, InlineFieldList, FieldList

import flask_admin.model.fields as f


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


class InstitutesForm(form.Form):
    """создаём форму"""
    name = fields.SelectField('Название', widget=Select2Widget())
    link = fields.StringField('Ссылка',[validators.DataRequired()])


class CoursesForm(form.Form):

    choices_institute = ['Аспирантура', 'Институт авиамашиностроения и транспорта', 'Институт архитектуры, строительства и дизайна',
                         'Институт высоких технологий', 'Институт заочно-вечернего обучения', 'Институт информационных технологий и анализа данных',
                         'Институт недропользования','Институт экономики, управления и права','Институт энергетики']
    choices_name = ['1 курс', '2 курс', '3 курс', '4 курс', '5 курс', '6 курс']
    institute = fields.SelectField('Институт',choices=choices_institute)
    name = fields.SelectField('Курс', choices=choices_name)


class InnerFormLessons(form.Form):
    name = fields.StringField()
    time = fields.StringField()
    week = fields.StringField()
    aud = fields.StringField()
    info = fields.StringField()
    prep = fields.StringField()



class InnerFormDays(form.Form):
    day = fields.StringField()
    lessons = InlineFieldList(InlineFormField(InnerFormLessons))#InlineFormField(InnerFormLessons)

class ScheduleForm(form.Form):
    group = fields.StringField('Группа')
    schedule = InlineFieldList(InlineFormField(InnerFormDays),'Расписание')


class GroupsForm(form.Form):
    choices_institute = ['Аспирантура', 'Институт авиамашиностроения и транспорта',
                         'Институт архитектуры, строительства и дизайна',
                         'Институт высоких технологий', 'Институт заочно-вечернего обучения',
                         'Институт информационных технологий и анализа данных',
                         'Институт недропользования', 'Институт экономики, управления и права', 'Институт энергетики']
    choices_course = ['1 курс', '2 курс', '3 курс', '4 курс', '5 курс', '6 курс']
    name = fields.SelectField('Название',widget=Select2Widget())
    institute = fields.SelectField('Институт',choices = choices_institute)
    link = fields.StringField('Ссылка', [validators.DataRequired()])
    course = fields.SelectField('Курс', choices = choices_course)
#
# TG bot admin
class BotSendMessageForm(form.Form):
    choices = ['Без шаблона', 'Важное сообщение', 'Информационное сообщение']
    template = fields.SelectField('Шаблон (добавляет текст в начале сообщения)', choices=choices)
    text = fields.TextAreaField(label='Текст сообщения', validators=[validators.DataRequired()])
    choices = ['Без клавиатуры', 'Основное меню']
    keyboard = fields.SelectField('Клавиатура', choices=choices)


