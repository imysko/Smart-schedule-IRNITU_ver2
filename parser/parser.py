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


# Получаем курс группы
def kurs(group) -> str:
    now = datetime.datetime.now()
    year = str(now.year)[2:4]  # получение двух последних цифр года 2020 - 20; 2021 - 21...
    month = now.month
    group_year = re.findall('(\d+)', group)  # получение года групп ИБб-18-1 = 18; ИБб-19-1 = 19...
    if (month > 8) and (month <= 12):
        course = int(year) + 1 - int(group_year[0])
    elif (month >= 1) and (month < 7):
        course = int(year) - int(group_year[0])
    return f'{course} курс'


def get_groups(html):
    """Возвращает группы и ссылки на них"""
    soup = BeautifulSoup(html, 'html.parser')
    groups = soup.find(class_='kurs-list')
    courses = groups.find_all('li')
    links = []
    groups_parse_list = []

    rd_groups_list = []

    # Получаем ссылки
    for link in soup.find_all('a'):
        if '?group=' in str(link):
            links.append('https://www.istu.edu/schedule/' + link.get('href'))

    # Получаем курсы
    for i in courses:
        if groups_parse_list == []:
            groups_parse_list.append(i.find('a').text)
        else:
            if i.find('a').text == groups_parse_list[-1]:
                continue
            else:
                groups_parse_list.append(i.find('a').text)

    for i in range(len(groups_parse_list)):
        rd_groups = {}
        rd_groups['course'] = kurs(group=groups_parse_list[i])
        rd_groups['name'] = groups_parse_list[i]
        rd_groups['link'] = links[i]
        rd_groups_list.append(rd_groups)

    return rd_groups_list


def count_course(html):
    """Получаем кол-во курсов"""
    soup = BeautifulSoup(html, 'html.parser')
    groups = soup.find(class_='kurs-list')
    count_courses = len(groups.find_all('ul'))
    course = []
    for i in range(1, count_courses + 1):
        course.append(f'{i} курс')

    return course


def parse():
    """старт бесконечного парсинга"""
    while True:
        start_time = time()  # начало парсинга

        # парсим институты
        html_institutes = get_html(url=URL_INSTITUTES)
        institutes = get_institutes(html=html_institutes)
        storage.save_institutes(institutes)
        print('==========ИНСТИТУТЫ==========')
        pprint(institutes)

        # парсим курсы
        courses = []
        for institute in institutes:
            html_count_course = get_html(url=institute['link'])
            course = count_course(html=html_count_course)
            institute_name = institute['name']
            for name in course:
                courses.append({'name': name, 'institute': institute_name})
        storage.save_courses(courses=courses)
        print('\n\n==========КУРСЫ==========')
        pprint(courses)

        # парсим группы
        all_groups = []
        for institute in institutes:
            html_groups = get_html(url=institute['link'])
            groups = get_groups(html=html_groups)
            for group in groups:
                group['institute'] = institute['name']
                all_groups.append(group)
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
        print(f'--- {time() - start_time} seconds ---')
        print('Waiting...')
        sleep(PARSE_TIME_HOURS * 60 * 60)


def main():
    parse()


if __name__ == '__main__':
    main()
