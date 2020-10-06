import requests
from bs4 import BeautifulSoup
from time import sleep, time
from pprint import pprint
import re
import os
from storage import MongodbService

URL_INSTITUTES = os.getenv('URL_INSTITUTES',
                           default='https://www.istu.edu/schedule/')  # Ссылка на страницу с институтами

PARSE_TIME_HOURS = int(os.getenv('PARSE_TIME_HOURS', default=1))  # время задержки парсинга (в часах)

storage = MongodbService().get_instance()


def get_html(url):
    """возвращает страницу по url"""
    response = requests.get(url)
    html = response.text
    # Если сайт недоступен или нашли пустую страницу
    if "Страница не найдена" in html or response.status_code != 200:
        # ждём и пробуем ещё раз
        sleep(10)
        response = requests.get(url)
        # если сайт недоступен или нашли пустую страницу
        if "Страница не найдена" in html or response.status_code != 200:
            # выбрасываем исключение
            raise Exception("Couldn't get html. Bad connection or URL\n"
                            f"URL: {url}")
    else:
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
        try:
            html_institutes = get_html(url=URL_INSTITUTES)
        except Exception as e:
            print(e)
            sleep(60)
            continue
        try:
            institutes = get_institutes(html=html_institutes)
        except Exception as e:
            print(e)
            continue

        # сохраняем в БД
        storage.save_institutes(institutes)
        print('==========ИНСТИТУТЫ==========')
        pprint(institutes)

        # парсим курсы и группы
        all_courses = []
        all_groups = []
        for institute in institutes:
            try:
                html_courses_and_croups = get_html(url=institute['link'])
            except Exception as e:
                print(e)
                continue

            try:
                courses, groups = get_courses_and_groups(html=html_courses_and_croups)
            except Exception as e:
                print(e)
                continue


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
            try:
                html_schedule_groups = get_html(url=group['link'])
            except Exception as e:
                print(e)
                continue

            try:
                schedule = get_schedule(html=html_schedule_groups)
            except Exception as e:
                print(e)
                continue

            group_schedule = {'group': group['name'], 'schedule': schedule}
            storage.save_schedule(group_schedule)  # сохраняем по одной группе
            pprint(group_schedule)

        # засыпаем
        parse_time = time() - start_time
        print(f'--- Parse time {parse_time} seconds ({parse_time / 60} minutes)---')
        print('Waiting...')
        sleep(PARSE_TIME_HOURS * 60 * 60)


if __name__ == '__main__':
    parse()
