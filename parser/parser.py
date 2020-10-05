import requests
from bs4 import BeautifulSoup
from time import sleep, time
from pprint import pprint
import re
import datetime
import os
from storage import MongodbService

URL_INSTITUTES = os.getenv('URL_INSTITUTES',
                           default='https://www.istu.edu/schedule/')  # Ссылка на страницу с институтами

PARSE_TIME_HOURS = int(os.getenv('PARSE_TIME_HOURS', default=1))  # время задержки парсинга (в часах)

storage = MongodbService().get_instance()


def get_html(url):
    """возвращает страницу по url"""
    response = requests.get(url)
    return response.text


def get_institutes(html):
    """Возвращает институты и ссылки на них"""
    soup = BeautifulSoup(html, 'html.parser')
    insts = soup.find(class_='content')
    inst = insts.find_all('li')
    inst_tags_list = []
    links = []

    rd_inst_list = []
    # Берём названия институтов
    for ins in inst:
        inst_tags_list.append(ins.find('a').text)
    # Берём ссылки
    for link in soup.find_all('a'):
        if '?subdiv' in str(link):
            links.append('https://www.istu.edu/schedule/' + link.get('href'))

    for i in range(len(inst_tags_list)):
        rd_inst = {}
        rd_inst['name'] = inst_tags_list[i]
        rd_inst['link'] = links[i]
        rd_inst_list.append(rd_inst)

    return rd_inst_list


def get_courses_and_groups(html):
    """Получаем курсы и группы"""
    soup = BeautifulSoup(html, 'html.parser')

    # находим все курсы в html по регулярному выражению
    courses = [course[5] + ' курс' for course in re.findall('Курс \d+', html)]

    groups_list = soup.find(class_='kurs-list').find_all('ul')

    groups = []
    # проходимся по всем курсам
    for course_groups, course in zip(groups_list, courses):
        # проходимся по всем группам в курсе
        for group in course_groups.find_all('li'):
            link = 'https://www.istu.edu/schedule/' + group.find('a').get('href')
            groups.append(
                {
                    'name': group.find('a').text,
                    'link': link,
                    'course': course,
                }
            )
    return courses, groups


def get_schedule(html):
    """возвращает расписание со страницы html"""
    soup = BeautifulSoup(html, 'html.parser')
    days = soup.find_all(class_='day-heading')
    lines = soup.find_all(class_='class-lines')

    schedule = []

    for line, day in zip(lines, days):
        one_day = {}
        lessons = []
        one_day['day'] = day.text.split(',')[0]  # берем только день недели (без даты)
        tails = line.find_all(class_='class-tails')
        for t in tails:
            time = t.find(class_='class-time').text
            tail = t.find_all(class_='class-tail')
            for item in tail:
                # определяем неделю
                if 'class-even-week' in str(item):
                    week = 'even'
                elif 'class-odd-week' in str(item):
                    week = 'odd'
                else:
                    week = 'all'
                inf = {}
                inf['time'] = time
                inf['week'] = week
                name = item.find(class_='class-pred')
                # смотрим есть ли занятие или свободно
                if not name:
                    inf['name'] = 'свободно'
                else:
                    inf['name'] = name.text
                    inf['aud'] = item.find(class_='class-aud').text
                    inf['info'] = item.find(class_='class-info').text
                    inf['prep'] = item.find('a').text

                lessons.append(inf)
        one_day['lessons'] = lessons
        schedule.append(one_day)

    return schedule


def parse():
    """старт бесконечного парсинга"""
    while True:
        start_time = time()  # начало парсинга

        # парсим институты
        html_institutes = get_html(url=URL_INSTITUTES)
        institutes = get_institutes(html=html_institutes)
        # сохраняем в БД
        storage.save_institutes(institutes)
        print('==========ИНСТИТУТЫ==========')
        pprint(institutes)

        # парсим курсы и группы
        all_courses = []
        all_groups = []
        for institute in institutes:
            html_courses_and_croups = get_html(url=institute['link'])

            courses, groups = get_courses_and_groups(html=html_courses_and_croups)

            institute_name = institute['name']
            for name in courses:
                all_courses.append({'name': name, 'institute': institute_name})

            for group in groups:
                group['institute'] = institute['name']
                all_groups.append(group)
        # сохраняем в БД
        storage.save_courses(courses=all_courses)
        print('\n\n==========КУРСЫ==========')
        pprint(all_courses)
        storage.save_groups(all_groups)
        print('\n\n==========ГРУППЫ==========')
        pprint(all_groups)

        # парсим расписание групп
        print('\n\n==========РАСПИСАНИЕ==========')

        for group in all_groups:
            html_schedule_groups = get_html(url=group['link'])
            schedule = get_schedule(html=html_schedule_groups)
            group_schedule = {'group': group['name'], 'schedule': schedule}
            storage.save_schedule(group_schedule)  # сохраняем по одной группе
            pprint(group_schedule)

        # засыпаем
        parse_time = time() - start_time
        print(f'--- Parse time {parse_time} seconds ({parse_time / 60}) minutes---')
        print('Waiting...')
        sleep(PARSE_TIME_HOURS * 60 * 60)


if __name__ == '__main__':
    parse()
