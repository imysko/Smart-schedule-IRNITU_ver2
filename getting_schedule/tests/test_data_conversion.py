import unittest
from unittest import mock

from data_conversion import convert_institutes, convert_groups, convert_courses, convert_schedule, \
    convert_teachers_schedule

from functions import schedule_tools

import datetime
import pytz

TIME_ZONE = pytz.timezone('Asia/Irkutsk')


class TestInstitutesConversionMethods(unittest.TestCase):

    def test_convert_institutes_oneDictInList(self):
        input_value = [{'fac': 'Аспирантура'}]
        expected = [{'name': 'Аспирантура'}]
        result = convert_institutes(input_value)
        self.assertEqual(result, expected)

    def test_convert_institutes_aFewDictInList(self):
        input_value = [
            {'fac': 'Институт авиамашиностроения и транспорта'},
            {'fac': 'Институт заочно-вечернего обучения'}
        ]
        expected = [
            {'name': 'Институт авиамашиностроения и транспорта'},
            {'name': 'Институт заочно-вечернего обучения'}
        ]
        result = convert_institutes(input_value)
        self.assertEqual(result, expected)

    def test_convert_institutes_emptyList_returnValueError(self):
        input_value = []
        with self.assertRaises(ValueError):
            convert_institutes(input_value)


class TestGroupsConversionMethods(unittest.TestCase):

    def test_convert_groups_oneDictInList(self):
        input_value = [{'obozn': 'ПСУм-20-1', 'kurs': 1, 'fac': 'Институт высоких технологий'}]
        expected = [{'name': 'ПСУм-20-1', 'course': '1 курс', 'institute': 'Институт высоких технологий'}]
        result = convert_groups(input_value)
        self.assertEqual(result, expected)

    def test_convert_groups_aFewDictInList(self):
        input_value = [
            {'obozn': 'ГРб-20-1', 'kurs': 1, 'fac': 'Институт архитектуры, строительства и дизайна'},
            {'obozn': 'ИГ-17-1', 'kurs': 4, 'fac': 'Институт недропользования'},
            {'obozn': 'УКбп-17-1', 'kurs': 4, 'fac': 'Институт высоких технологий'}
        ]
        expected = [
            {'name': 'ГРб-20-1', 'course': '1 курс', 'institute': 'Институт архитектуры, строительства и дизайна'},
            {'name': 'ИГ-17-1', 'course': '4 курс', 'institute': 'Институт недропользования'},
            {'name': 'УКбп-17-1', 'course': '4 курс', 'institute': 'Институт высоких технологий'}
        ]
        result = convert_groups(input_value)
        self.assertEqual(result, expected)

    def test_convert_groups_emptyList_returnValueError(self):
        input_value = []
        with self.assertRaises(ValueError):
            convert_groups(input_value)


class TestCoursesConversionMethods(unittest.TestCase):

    def test_convert_courses_aFewDictInList(self):
        input_value = [
            {'name': 'УКбп-17-1', 'course': '4 курс', 'institute': 'Институт высоких технологий'},
            {'name': 'УВФ-17-1', 'course': '4 курс', 'institute': 'Институт недропользования'},
            {'name': 'ГРб-20-1', 'course': '1 курс', 'institute': 'Институт архитектуры, строительства и дизайна'},
            {'name': 'УКбп-19-1', 'course': '2 курс', 'institute': 'Институт высоких технологий'},
            {'name': 'ИГ-18-1', 'course': '3 курс', 'institute': 'Институт недропользования'},
            {'name': 'йцу-18-1', 'course': '3 курс', 'institute': 'Институт недропользования'},
            {'name': 'фывв-18-1', 'course': '3 курс', 'institute': 'Институт недропользования'},
            {'name': 'АБВб-17-1', 'course': '4 курс', 'institute': 'Институт высоких технологий'}
        ]
        expected = [
            {'name': '4 курс', 'institute': 'Институт высоких технологий'},
            {'name': '4 курс', 'institute': 'Институт недропользования'},
            {'name': '1 курс', 'institute': 'Институт архитектуры, строительства и дизайна'},
            {'name': '2 курс', 'institute': 'Институт высоких технологий'},
            {'name': '3 курс', 'institute': 'Институт недропользования'},
        ]
        result = convert_courses(input_value)
        self.assertEqual(result, expected)

    def test_convert_courses_emptyList_returnValueError(self):
        input_value = []
        with self.assertRaises(ValueError):
            convert_courses(input_value)


class TestScheduleToolsMethods(unittest.TestCase):
    def test_getting_week_and_day_of_week_pqLesson_retunAllPonedelnick(self):
        input_value = {
            'obozn': '',
            'begtime': '10:00',
            'everyweek': 2,
            'preps': '',
            'auditories_verbose': '',
            'day': 1,
            'nt': None,
            'title': '',
            'ngroup': None,
            'dend': datetime.date(2021, 4, 12)
        }
        expected = ('all', 'понедельник')

        result = schedule_tools.getting_week_and_day_of_week(input_value)
        self.assertEqual(result, expected)

    def test_is_there_dict_with_value_in_list_ListWithDictWithKey_true(self):
        input_value_list = [
            {'dadsa': '', 'day': 'right_value'},
            {'day': '', 'asd': 12},
            {'day': {}}
        ]

        input_value_key = 'right_value'
        result = schedule_tools.is_there_dict_with_value_in_list(input_value_list, input_value_key)
        self.assertTrue(result)

    def test_forming_info_data_NtAndNgroup_returnInfoLekcia(self):
        input_value_nt = 1
        input_value_ngroup = None

        expected = '( Лекция )'

        result = schedule_tools.forming_info_data(nt=input_value_nt, ngroup=input_value_ngroup)
        self.assertEqual(result, expected)

    def test_forming_info_data_NtAndNgroup_returnInfoPraktika(self):
        input_value_nt = 2
        input_value_ngroup = 1

        expected = '( Практ. подгруппа 1 )'

        result = schedule_tools.forming_info_data(nt=input_value_nt, ngroup=input_value_ngroup)
        self.assertEqual(result, expected)

    def test_forming_info_data_NtAndNgroup_returnInfoLaba(self):
        input_value_nt = 3
        input_value_ngroup = 2

        expected = '( Лаб. раб. подгруппа 2 )'

        result = schedule_tools.forming_info_data(nt=input_value_nt, ngroup=input_value_ngroup)
        self.assertEqual(result, expected)


class TestScheduleConversionMethods(unittest.TestCase):

    # Расписание

    @mock.patch('data_conversion.datetime')
    def test_convert_schedule_ListWithDictWithOboznAndInfo_returnListWithDictWithGroupAndSchedule(self, mock_dt):
        mock_dt.now(TIME_ZONE).date = mock.Mock(return_value=datetime.date(2021, 1, 15))

        input_value = [
            {'obozn': '', 'begtime': '10:00', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 1,
             'nt': 1, 'title': '', 'ngroup': None, 'dend': datetime.date(2021, 4, 12)},
        ]
        example_expected_list = [
            {
                'group': '',
                'schedule': []
            }
        ]

        result = convert_schedule(input_value)

        # Проверяем, что содержит словарь из двух элементов
        expected = 2
        self.assertEqual(len(result[0]), expected)

        # Проверяем, что есть ключ group
        self.assertIsNotNone(result[0].get('group'))

        # Проверяем, что есть ключ schedule
        self.assertIsNotNone(result[0].get('schedule'))

    @mock.patch('data_conversion.datetime')
    def test_convert_schedule_pqScheduleList_returnMgListWithRightGroup(self, mock_dt):
        mock_dt.now(TIME_ZONE).date = mock.Mock(return_value=datetime.date(2021, 1, 15))

        input_value = [
            {'obozn': 'АРбв-17-1', 'begtime': '10:00', 'everyweek': 1,
             'preps': '', 'auditories_verbose': '', 'day': 2,
             'nt': 1, 'title': '', 'ngroup': None, 'dend': datetime.date(2021, 4, 12)},
        ]

        expected = 'АРбв-17-1'
        result = convert_schedule(input_value)[0]['group']
        self.assertEqual(result, expected)

    @mock.patch('data_conversion.datetime')
    def test_convert_schedule_pqScheduleList_returnIsScheduleList(self, mock_dt):
        mock_dt.now(TIME_ZONE).date = mock.Mock(return_value=datetime.date(2021, 1, 15))

        input_value = [
            {'obozn': '', 'begtime': '10:00', 'everyweek': 1,
             'preps': '', 'auditories_verbose': '', 'day': 2,
             'nt': 1, 'title': '', 'ngroup': None, 'dend': datetime.date(2021, 4, 12)},
        ]

        expected = type([])
        result = type(convert_schedule(input_value)[0]['schedule'])
        self.assertEqual(result, expected)

    @mock.patch('data_conversion.datetime')
    def test_convert_schedule_pqScheduleList_returnDictWithDayAndLessos(self, mock_dt):
        mock_dt.now(TIME_ZONE).date = mock.Mock(return_value=datetime.date(2021, 1, 15))

        input_value = [
            {'obozn': '', 'begtime': '10:00', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 1,
             'nt': 1, 'title': '', 'ngroup': None, 'dend': datetime.date(2021, 4, 12)},
        ]
        example_expected_list = [
            {
                'group': '',
                'schedule': [
                    {
                        'day': '',
                        'lessons': []
                    }
                ]
            }
        ]

        result = convert_schedule(input_value)

        # Проверяем, что schedule содержит словарь из двух элементов
        expected = 2
        self.assertEqual(len(result[0]['schedule'][0]), expected)

        # Проверяем, что есть ключ day
        self.assertIsNotNone(result[0]['schedule'][0].get('day'))

        # Проверяем, что есть ключ lessons
        self.assertIsNotNone(result[0]['schedule'][0].get('lessons'))

    @mock.patch('data_conversion.datetime')
    def test_convert_schedule_pqScheduleList_returnRightDay(self, mock_dt):
        mock_dt.now(TIME_ZONE).date = mock.Mock(return_value=datetime.date(2021, 1, 15))

        input_value = [
            {'obozn': '', 'begtime': '10:00', 'everyweek': 1,
             'preps': '', 'auditories_verbose': '', 'day': 2,
             'nt': 1, 'title': '', 'ngroup': None, 'dend': datetime.date(2021, 4, 12)},
        ]

        expected = 'вторник'
        result = convert_schedule(input_value)[0]['schedule'][0]['day']
        self.assertEqual(result, expected)

    @mock.patch('data_conversion.datetime')
    def test_convert_schedule_pqScheduleList_returnIsLessonsList(self, mock_dt):
        mock_dt.now(TIME_ZONE).date = mock.Mock(return_value=datetime.date(2021, 1, 15))

        input_value = [
            {'obozn': '', 'begtime': '10:00', 'everyweek': 1,
             'preps': '', 'auditories_verbose': '', 'day': 2,
             'nt': 1, 'title': '', 'ngroup': None, 'dend': datetime.date(2021, 4, 12)},
        ]

        expected = type([])
        result = type(convert_schedule(input_value)[0]['schedule'][0]['lessons'])
        self.assertEqual(result, expected)

    @mock.patch('data_conversion.datetime')
    def test_convert_schedule_pqScheduleList_returnLessonDictWithTimeWeekNameAudInfoPrep(self, mock_dt):
        mock_dt.now(TIME_ZONE).date = mock.Mock(return_value=datetime.date(2021, 1, 15))

        input_value = [
            {'obozn': '', 'begtime': '10:00', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 1,
             'nt': 1, 'title': '', 'ngroup': None, 'dend': datetime.date(2021, 4, 12)},
        ]
        example_expected_list = [
            {
                'group': '',
                'schedule': [
                    {
                        'day': '',
                        'lessons': [
                            {
                                'time': '',
                                'week': '',
                                'name': '',
                                'aud': '',
                                'info': '',
                                'prep': '',
                            }
                        ]
                    }
                ]
            }
        ]

        result = convert_schedule(input_value)

        # Проверяем, что lessons содержит словарь из двух элементов
        expected = 6
        self.assertEqual(len(result[0]['schedule'][0]['lessons'][0]), expected)

        # Проверяем, что есть ключ time
        self.assertIsNotNone(result[0]['schedule'][0]['lessons'][0].get('time'))

        # Проверяем, что есть ключ week
        self.assertIsNotNone(result[0]['schedule'][0]['lessons'][0].get('week'))

        # Проверяем, что есть ключ name
        self.assertIsNotNone(result[0]['schedule'][0]['lessons'][0].get('name'))

        # Проверяем, что есть ключ aud
        self.assertIsNotNone(result[0]['schedule'][0]['lessons'][0].get('aud'))

        # Проверяем, что есть ключ info
        self.assertIsNotNone(result[0]['schedule'][0]['lessons'][0].get('info'))

        # Проверяем, что есть ключ prep
        self.assertIsNotNone(result[0]['schedule'][0]['lessons'][0].get('prep'))

    @mock.patch('data_conversion.datetime')
    def test_convert_schedule_oneDictInListLekciaAll(self, mock_dt):
        mock_dt.now(TIME_ZONE).date = mock.Mock(return_value=datetime.date(2021, 1, 15))

        input_value = [
            {'obozn': 'ТХб-18-2',
             'begtime': '10:00',
             'everyweek': 2,
             'preps': 'Лобацкая Раиса Моисеевна                           ',
             'auditories_verbose': 'И-311',
             'day': 1,
             'nt': 1,
             'title': 'История искусств',
             'ngroup': None,
             'dend': datetime.date(2021, 4, 12)
             }
        ]
        expected = [
            {
                'group': 'ТХб-18-2',
                'schedule': [
                    {
                        'day': 'понедельник',
                        'lessons': [
                            {
                                'time': '10:00',
                                'week': 'all',
                                'name': 'История искусств',
                                'aud': 'И-311',
                                'info': '( Лекция )',
                                'prep': 'Лобацкая Раиса Моисеевна',
                            }
                        ]
                    }
                ]
            }
        ]
        result = convert_schedule(input_value)
        self.assertEqual(result, expected)

    @mock.patch('data_conversion.datetime')
    def test_convert_schedule_oneDictInListLabaEven(self, mock_dt):
        mock_dt.now(TIME_ZONE).date = mock.Mock(return_value=datetime.date(2021, 1, 15))

        input_value = [
            {'obozn': 'ТХб-18-1',
             'begtime': '11:45',
             'everyweek': 1,
             'preps': 'Юрьева Лена Валерьевна                             ',
             'auditories_verbose': 'Е-215б',
             'day': 2,
             'nt': 3,
             'title': 'Минералогия ювелирных камней',
             'ngroup': 1,
             'dend': datetime.date(2021, 4, 12)}
        ]
        expected = [
            {
                'group': 'ТХб-18-1',
                'schedule': [
                    {
                        'day': 'вторник',
                        'lessons': [
                            {
                                'time': '11:45',
                                'week': 'even',
                                'name': 'Минералогия ювелирных камней',
                                'aud': 'Е-215б',
                                'info': '( Лаб. раб. подгруппа 1 )',
                                'prep': 'Юрьева Лена Валерьевна',
                            }
                        ]
                    }
                ]
            }
        ]
        result = convert_schedule(input_value)
        self.assertEqual(result, expected)

    def test_getting_week_and_day_of_week_pqLesson_retunEvenSreda(self):
        input_value = {
            'obozn': '',
            'begtime': '10:00',
            'everyweek': 1,
            'preps': '',
            'auditories_verbose': '',
            'day': 3,
            'nt': None,
            'title': '',
            'ngroup': None,
            'dend': datetime.date(2021, 4, 12)
        }
        expected = ('even', 'среда')

        result = schedule_tools.getting_week_and_day_of_week(input_value)
        self.assertEqual(result, expected)

    def test_getting_week_and_day_of_week_pqLesson_retunOddPatnica(self):
        input_value = {
            'obozn': '',
            'begtime': '10:00',
            'everyweek': 1,
            'preps': '',
            'auditories_verbose': '',
            'day': 12,
            'nt': None,
            'title': '',
            'ngroup': None,
            'dend': datetime.date(2021, 4, 12)
        }
        expected = ('odd', 'пятница')

        result = schedule_tools.getting_week_and_day_of_week(input_value)
        self.assertEqual(result, expected)

    def test_is_there_dict_with_value_in_list_ListWithDictWithoutKey_false(self):
        input_value_list = [
            {'dda': '', 'day': []},
            {'day': 'cxxc', 'sa': 12},
            {'day': {}}
        ]

        input_value_key = 'right_value'
        result = schedule_tools.is_there_dict_with_value_in_list(input_value_list, input_value_key)
        self.assertFalse(result)

    def test_is_there_dict_with_value_in_list_EmptyList_false(self):
        input_value_list = []

        input_value_key = 'right_value'
        result = schedule_tools.is_there_dict_with_value_in_list(input_value_list, input_value_key)
        self.assertFalse(result)

    @mock.patch('data_conversion.datetime')
    def test_convert_schedule_aFewDictInListOneGroup_DaysInRightOrder(self, mock_dt):
        mock_dt.now(TIME_ZONE).date = mock.Mock(return_value=datetime.date(2021, 1, 15))

        input_value = [
            {'obozn': 'ТХб-18-2', 'begtime': '10:00', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 3,
             'nt': 1, 'title': 'les_4', 'ngroup': None, 'dend': datetime.date(2021, 4, 12)},
            {'obozn': 'ТХб-18-2', 'begtime': '10:00', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 1,
             'nt': 1, 'title': 'les_1', 'ngroup': None, 'dend': datetime.date(2021, 4, 12)},
            {'obozn': 'ТХб-18-2', 'begtime': '10:00', 'everyweek': 1,
             'preps': '', 'auditories_verbose': '', 'day': 10,
             'nt': 1, 'title': 'les_5', 'ngroup': None, 'dend': datetime.date(2021, 4, 12)},
            {'obozn': 'ТХб-18-2', 'begtime': '10:00', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 1,
             'nt': 1, 'title': 'les_2', 'ngroup': None, 'dend': datetime.date(2021, 4, 12)},
            {'obozn': 'ТХб-18-2', 'begtime': '10:00', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 4,
             'nt': 1, 'title': 'les_6', 'ngroup': None, 'dend': datetime.date(2021, 4, 12)},
            {'obozn': 'ТХб-18-2', 'begtime': '10:00', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 6,
             'nt': 1, 'title': 'les_8', 'ngroup': None, 'dend': datetime.date(2021, 4, 12)},
            {'obozn': 'ТХб-18-2', 'begtime': '10:00', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 5,
             'nt': 1, 'title': 'les_7', 'ngroup': None, 'dend': datetime.date(2021, 4, 12)},
            {'obozn': 'ТХб-18-2', 'begtime': '10:00', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 2,
             'nt': 1, 'title': 'les_3', 'ngroup': None, 'dend': datetime.date(2021, 4, 12)}

        ]
        expected = [
            {
                'group': 'ТХб-18-2',
                'schedule': [
                    {
                        'day': 'понедельник',
                        'lessons': [
                            {
                                'time': '10:00',
                                'week': 'all',
                                'name': 'les_1',
                                'aud': '',
                                'info': '( Лекция )',
                                'prep': '',
                            },
                            {
                                'time': '10:00',
                                'week': 'all',
                                'name': 'les_2',
                                'aud': '',
                                'info': '( Лекция )',
                                'prep': '',
                            }
                        ],
                    },
                    {
                        'day': 'вторник',
                        'lessons': [
                            {
                                'time': '10:00',
                                'week': 'all',
                                'name': 'les_3',
                                'aud': '',
                                'info': '( Лекция )',
                                'prep': '',
                            }
                        ],
                    },
                    {
                        'day': 'среда',
                        'lessons': [
                            {
                                'time': '10:00',
                                'week': 'all',
                                'name': 'les_4',
                                'aud': '',
                                'info': '( Лекция )',
                                'prep': '',
                            },
                            {
                                'time': '10:00',
                                'week': 'odd',
                                'name': 'les_5',
                                'aud': '',
                                'info': '( Лекция )',
                                'prep': '',
                            }
                        ],
                    },
                    {
                        'day': 'четверг',
                        'lessons': [
                            {
                                'time': '10:00',
                                'week': 'all',
                                'name': 'les_6',
                                'aud': '',
                                'info': '( Лекция )',
                                'prep': '',
                            }
                        ],
                    },
                    {
                        'day': 'пятница',
                        'lessons': [
                            {
                                'time': '10:00',
                                'week': 'all',
                                'name': 'les_7',
                                'aud': '',
                                'info': '( Лекция )',
                                'prep': '',
                            }
                        ],
                    },
                    {
                        'day': 'суббота',
                        'lessons': [
                            {
                                'time': '10:00',
                                'week': 'all',
                                'name': 'les_8',
                                'aud': '',
                                'info': '( Лекция )',
                                'prep': '',
                            }
                        ],
                    }
                ]
            }
        ]
        result = convert_schedule(input_value)
        self.assertEqual(result, expected)

    @mock.patch('data_conversion.datetime')
    def test_convert_schedule_aFewDictInListOneDay_LessonsInRightOrder(self, mock_dt):
        mock_dt.now(TIME_ZONE).date = mock.Mock(return_value=datetime.date(2021, 1, 15))

        input_value = [
            {'obozn': 'ТХб-18-2', 'begtime': '18:45', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 3,
             'nt': 1, 'title': 'les_4', 'ngroup': None, 'dend': datetime.date(2021, 4, 12)},
            {'obozn': 'ТХб-18-2', 'begtime': '10:00', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 3,
             'nt': 1, 'title': 'les_2', 'ngroup': None, 'dend': datetime.date(2021, 4, 12)},
            {'obozn': 'ТХб-18-2', 'begtime': '11:45', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 3,
             'nt': 1, 'title': 'les_3', 'ngroup': None, 'dend': datetime.date(2021, 4, 12)},
            {'obozn': 'ТХб-18-2', 'begtime': '8:15', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 3,
             'nt': 1, 'title': 'les_1', 'ngroup': None, 'dend': datetime.date(2021, 4, 12)},
        ]

        expected = [
            {
                'group': 'ТХб-18-2',
                'schedule': [
                    {
                        'day': 'среда',
                        'lessons': [
                            {
                                'time': '8:15',
                                'week': 'all',
                                'name': 'les_1',
                                'aud': '',
                                'info': '( Лекция )',
                                'prep': '',
                            },
                            {
                                'time': '10:00',
                                'week': 'all',
                                'name': 'les_2',
                                'aud': '',
                                'info': '( Лекция )',
                                'prep': '',
                            },
                            {
                                'time': '11:45',
                                'week': 'all',
                                'name': 'les_3',
                                'aud': '',
                                'info': '( Лекция )',
                                'prep': '',
                            },
                            {
                                'time': '18:45',
                                'week': 'all',
                                'name': 'les_4',
                                'aud': '',
                                'info': '( Лекция )',
                                'prep': '',
                            }
                        ]
                    }
                ]
            }
        ]

        result = convert_schedule(input_value)
        self.assertEqual(result, expected)

    @mock.patch('data_conversion.datetime')
    def test_convert_schedule_aFewDictInListOneDay_SubgroupsInRightOrder(self, mock_dt):
        mock_dt.now(TIME_ZONE).date = mock.Mock(return_value=datetime.date(2021, 1, 15))

        input_value = [
            {'obozn': 'ТХб-18-2', 'begtime': '10:00', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 3,
             'nt': 2, 'title': 'les_2', 'ngroup': 2, 'dend': datetime.date(2021, 4, 12)},
            {'obozn': 'ТХб-18-2', 'begtime': '10:00', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 3,
             'nt': 2, 'title': 'les_1', 'ngroup': 1, 'dend': datetime.date(2021, 4, 12)},
            {'obozn': 'ТХб-18-2', 'begtime': '11:45', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 3,
             'nt': 3, 'title': 'les_4', 'ngroup': 2, 'dend': datetime.date(2021, 4, 12)},
            {'obozn': 'ТХб-18-2', 'begtime': '11:45', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 3,
             'nt': 3, 'title': 'les_3', 'ngroup': 1, 'dend': datetime.date(2021, 4, 12)},
        ]

        expected = [
            {
                'group': 'ТХб-18-2',
                'schedule': [
                    {
                        'day': 'среда',
                        'lessons': [
                            {
                                'time': '10:00',
                                'week': 'all',
                                'name': 'les_1',
                                'aud': '',
                                'info': '( Практ. подгруппа 1 )',
                                'prep': '',
                            },
                            {
                                'time': '10:00',
                                'week': 'all',
                                'name': 'les_2',
                                'aud': '',
                                'info': '( Практ. подгруппа 2 )',
                                'prep': '',
                            },
                            {
                                'time': '11:45',
                                'week': 'all',
                                'name': 'les_3',
                                'aud': '',
                                'info': '( Лаб. раб. подгруппа 1 )',
                                'prep': '',
                            },
                            {
                                'time': '11:45',
                                'week': 'all',
                                'name': 'les_4',
                                'aud': '',
                                'info': '( Лаб. раб. подгруппа 2 )',
                                'prep': '',
                            }
                        ]
                    }
                ]
            }
        ]

        result = convert_schedule(input_value)
        self.assertEqual(result, expected)

    @mock.patch('data_conversion.datetime')
    def test_convert_schedule_aFewDictInListOneDay_RightInfo(self, mock_dt):
        mock_dt.now(TIME_ZONE).date = mock.Mock(return_value=datetime.date(2021, 1, 15))

        input_value = [
            {'obozn': 'ТХб-18-2', 'begtime': '10:01', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 3,
             'nt': 1, 'title': 'les_1', 'ngroup': None, 'dend': datetime.date(2021, 4, 12)},
            {'obozn': 'ТХб-18-2', 'begtime': '10:03', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 3,
             'nt': 2, 'title': 'les_3', 'ngroup': 2, 'dend': datetime.date(2021, 4, 12)},
            {'obozn': 'ТХб-18-2', 'begtime': '10:02', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 3,
             'nt': 2, 'title': 'les_2', 'ngroup': 1, 'dend': datetime.date(2021, 4, 12)},
            {'obozn': 'ТХб-18-2', 'begtime': '10:04', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 3,
             'nt': 2, 'title': 'les_4', 'ngroup': None, 'dend': datetime.date(2021, 4, 12)},
            {'obozn': 'ТХб-18-2', 'begtime': '10:05', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 3,
             'nt': 3, 'title': 'les_5', 'ngroup': 1, 'dend': datetime.date(2021, 4, 12)},
            {'obozn': 'ТХб-18-2', 'begtime': '10:06', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 3,
             'nt': 3, 'title': 'les_6', 'ngroup': 2, 'dend': datetime.date(2021, 4, 12)},
            {'obozn': 'ТХб-18-2', 'begtime': '10:07', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 3,
             'nt': 3, 'title': 'les_7', 'ngroup': None, 'dend': datetime.date(2021, 4, 12)},
        ]

        expected = [
            {
                'group': 'ТХб-18-2',
                'schedule': [
                    {
                        'day': 'среда',
                        'lessons': [
                            {
                                'time': '10:01',
                                'week': 'all',
                                'name': 'les_1',
                                'aud': '',
                                'info': '( Лекция )',
                                'prep': '',
                            },
                            {
                                'time': '10:02',
                                'week': 'all',
                                'name': 'les_2',
                                'aud': '',
                                'info': '( Практ. подгруппа 1 )',
                                'prep': '',
                            },
                            {
                                'time': '10:03',
                                'week': 'all',
                                'name': 'les_3',
                                'aud': '',
                                'info': '( Практ. подгруппа 2 )',
                                'prep': '',
                            },
                            {
                                'time': '10:04',
                                'week': 'all',
                                'name': 'les_4',
                                'aud': '',
                                'info': '( Практ. )',
                                'prep': '',
                            },
                            {
                                'time': '10:05',
                                'week': 'all',
                                'name': 'les_5',
                                'aud': '',
                                'info': '( Лаб. раб. подгруппа 1 )',
                                'prep': '',
                            },
                            {
                                'time': '10:06',
                                'week': 'all',
                                'name': 'les_6',
                                'aud': '',
                                'info': '( Лаб. раб. подгруппа 2 )',
                                'prep': '',
                            },
                            {
                                'time': '10:07',
                                'week': 'all',
                                'name': 'les_7',
                                'aud': '',
                                'info': '( Лаб. раб. )',
                                'prep': '',
                            }
                        ]
                    }
                ]
            }
        ]

        result = convert_schedule(input_value)
        self.assertEqual(result, expected)

    @mock.patch('data_conversion.datetime')
    def test_convert_schedule_aFewDictInListOneDay_RightPrepAndAud(self, mock_dt):
        mock_dt.now(TIME_ZONE).date = mock.Mock(return_value=datetime.date(2021, 1, 15))

        input_value = [
            {'obozn': 'ТХб-18-2', 'begtime': '10:00', 'everyweek': 2,
             'preps': 'Пупкин Вася', 'auditories_verbose': 'Ж-313', 'day': 6,
             'nt': 1, 'title': 'les_1', 'ngroup': None, 'dend': datetime.date(2021, 4, 12)}
        ]

        expected = [
            {
                'group': 'ТХб-18-2',
                'schedule': [
                    {
                        'day': 'суббота',
                        'lessons': [
                            {
                                'time': '10:00',
                                'week': 'all',
                                'name': 'les_1',
                                'aud': 'Ж-313',
                                'info': '( Лекция )',
                                'prep': 'Пупкин Вася',
                            },
                        ]
                    }
                ]
            }
        ]

        result = convert_schedule(input_value)
        self.assertEqual(result, expected)

    @mock.patch('data_conversion.datetime')
    def test_convert_schedule_aFewDictInListOneDay_returnDuplicateLessonsRemoved(self, mock_dt):
        mock_dt.now(TIME_ZONE).date = mock.Mock(return_value=datetime.date(2021, 1, 5))

        input_value = [
            {'obozn': 'ИБб-18-1', 'begtime': '10:00', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 3,
             'nt': 2, 'title': 'les_1', 'ngroup': 1, 'dend': datetime.date(2020, 2, 19)},
            {'obozn': 'ИБб-18-1', 'begtime': '11:45', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 3,
             'nt': 1, 'title': 'les_2', 'ngroup': None, 'dend': datetime.date(2021, 1, 16)},
            {'obozn': 'ИБб-18-1', 'begtime': '10:00', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 3,
             'nt': 2, 'title': 'les_1', 'ngroup': 1, 'dend': datetime.date(2021, 1, 16)},
        ]

        expected = [
            {
                'group': 'ИБб-18-1',
                'schedule': [
                    {
                        'day': 'среда',
                        'lessons': [
                            {
                                'time': '10:00',
                                'week': 'all',
                                'name': 'les_1',
                                'aud': '',
                                'info': '( Практ. подгруппа 1 )',
                                'prep': '',
                            },
                            {
                                'time': '11:45',
                                'week': 'all',
                                'name': 'les_2',
                                'aud': '',
                                'info': '( Лекция )',
                                'prep': '',
                            }
                        ]
                    }
                ]
            }
        ]

        result = convert_schedule(input_value)
        self.assertEqual(result, expected)

    @mock.patch('data_conversion.datetime')
    def test_convert_schedule_PgScheduleWithCurrentDate_returnMongoSchedule(self, mock_dt):
        # Устанавливаем текущее время.
        mock_dt.now(TIME_ZONE).date = mock.Mock(return_value=datetime.date(2021, 1, 15))

        input_value = [
            {'obozn': 'ИБб-18-1', 'begtime': '10:00', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 3,
             'nt': 2, 'title': 'les_1', 'ngroup': 1, 'dend': datetime.date(2021, 1, 16)},
        ]

        expected = [
            {
                'group': 'ИБб-18-1',
                'schedule': [
                    {
                        'day': 'среда',
                        'lessons': [
                            {
                                'time': '10:00',
                                'week': 'all',
                                'name': 'les_1',
                                'aud': '',
                                'info': '( Практ. подгруппа 1 )',
                                'prep': '',
                            },
                        ]
                    }
                ]
            }
        ]

        result = convert_schedule(input_value)
        self.assertEqual(result, expected)

    @mock.patch('data_conversion.datetime')
    def test_convert_schedule_PgScheduleWithNotValidDate_returnEmptyList(self, mock_dt):
        # Устанавливаем текущее время.
        mock_dt.now(TIME_ZONE).date = mock.Mock(return_value=datetime.date(2021, 1, 17))

        input_value = [
            {'obozn': 'ИБб-18-1', 'begtime': '10:00', 'everyweek': 2,
             'preps': '', 'auditories_verbose': '', 'day': 3,
             'nt': 2, 'title': 'les_1', 'ngroup': 1, 'dend': datetime.date(2021, 1, 16)},
        ]

        expected = []

        result = convert_schedule(input_value)
        self.assertEqual(result, expected)


class TestTeachersScheduleConversionMethods(unittest.TestCase):
    """Расписание преподавателей."""

    @mock.patch('data_conversion.datetime')
    def test_convert_teachers_schedule_PgScheduleOneTeacherTwoLessons_returnMongoSchedule(self, mock_dt):
        # Устанавливаем текущее время.
        mock_dt.now(TIME_ZONE).date = mock.Mock(return_value=datetime.date(2021, 1, 15))

        input_value = [
            {'obozn': 'ИБб-18-1', 'begtime': '10:00', 'everyweek': 2,
             'preps': 'Преп 1   ', 'prep_short_name': 'Преп В.В.    ',
             'prep_id': 123, 'auditories_verbose': '', 'day': 3,
             'nt': 1, 'title': 'les_1', 'ngroup': None, 'dend': datetime.date(2021, 1, 16)},
            {'obozn': 'ИБб-18-2', 'begtime': '10:00', 'everyweek': 2,
             'preps': 'Преп 1   ', 'prep_short_name': 'Преп В.В.    ',
             'prep_id': 123, 'auditories_verbose': '', 'day': 3,
             'nt': 1, 'title': 'les_1', 'ngroup': None, 'dend': datetime.date(2021, 1, 16)},
            {'obozn': 'ИБб-18-1', 'begtime': '11:45', 'everyweek': 2,
             'preps': 'Преп 1   ', 'prep_short_name': 'Преп В.В.    ',
             'prep_id': 123, 'auditories_verbose': '', 'day': 3,
             'nt': 2, 'title': 'les_2', 'ngroup': 1, 'dend': datetime.date(2021, 1, 16)}
        ]

        expected = [
            {
                'prep': 'Преп 1',
                'prep_short_name': 'Преп В.В.',
                'pg_id': 123,
                'schedule': [
                    {
                        'day': 'среда',
                        'lessons': [
                            {
                                'time': '10:00',
                                'week': 'all',
                                'name': 'les_1',
                                'aud': '',
                                'info': '( Лекция )',
                                'groups': ['ИБб-18-1', 'ИБб-18-2']
                            },
                            {
                                'time': '11:45',
                                'week': 'all',
                                'name': 'les_2',
                                'aud': '',
                                'info': '( Практ. подгруппа 1 )',
                                'groups': ['ИБб-18-1']
                            },
                        ]
                    }
                ]
            }
        ]

        result = convert_teachers_schedule(input_value)
        self.assertEqual(result, expected)

    @mock.patch('data_conversion.datetime')
    def test_convert_teachers_schedule_PgScheduleTwoTeacher_returnMongoSchedule(self, mock_dt):
        # Устанавливаем текущее время.
        mock_dt.now(TIME_ZONE).date = mock.Mock(return_value=datetime.date(2021, 1, 15))

        input_value = [
            {'obozn': 'ИБб-18-1', 'begtime': '10:00', 'everyweek': 2,
             'preps': 'Преп 1   ', 'prep_short_name': 'Преп В.В.    ',
             'prep_id': 123, 'auditories_verbose': '', 'day': 3,
             'nt': 1, 'title': 'les_1', 'ngroup': None, 'dend': datetime.date(2021, 1, 16)},
            {'obozn': 'ИБб-18-2', 'begtime': '10:00', 'everyweek': 2,
             'preps': 'Преп 2   ', 'prep_short_name': 'Преп 2 A.A.    ',
             'prep_id': 456, 'auditories_verbose': '', 'day': 3,
             'nt': 1, 'title': 'les_2', 'ngroup': None, 'dend': datetime.date(2021, 1, 16)},
            {'obozn': 'ИБб-18-1', 'begtime': '11:45', 'everyweek': 2,
             'preps': 'Преп 1   ', 'prep_short_name': 'Преп В.В.    ',
             'prep_id': 123, 'auditories_verbose': '', 'day': 3,
             'nt': 2, 'title': 'les_3', 'ngroup': 1, 'dend': datetime.date(2021, 1, 16)}
        ]

        expected = [
            {
                'prep': 'Преп 1',
                'prep_short_name': 'Преп В.В.',
                'pg_id': 123,
                'schedule': [
                    {
                        'day': 'среда',
                        'lessons': [
                            {
                                'time': '10:00',
                                'week': 'all',
                                'name': 'les_1',
                                'aud': '',
                                'info': '( Лекция )',
                                'groups': ['ИБб-18-1']
                            },
                            {
                                'time': '11:45',
                                'week': 'all',
                                'name': 'les_3',
                                'aud': '',
                                'info': '( Практ. подгруппа 1 )',
                                'groups': ['ИБб-18-1']
                            },
                        ]
                    }
                ]
            },

            {
                'prep': 'Преп 2',
                'prep_short_name': 'Преп 2 A.A.',
                'pg_id': 456,
                'schedule': [
                    {
                        'day': 'среда',
                        'lessons': [
                            {
                                'time': '10:00',
                                'week': 'all',
                                'name': 'les_2',
                                'aud': '',
                                'info': '( Лекция )',
                                'groups': ['ИБб-18-2']
                            },
                        ]
                    }
                ]
            },
        ]

        result = convert_teachers_schedule(input_value)
        self.assertEqual(result, expected)

    @mock.patch('data_conversion.datetime')
    def test_convert_schedule_PgScheduleWithNotValidDate_returnEmptyList(self, mock_dt):
        # Устанавливаем текущее время.
        mock_dt.now(TIME_ZONE).date = mock.Mock(return_value=datetime.date(2021, 1, 17))

        input_value = [
            {'obozn': 'ИБб-18-1', 'begtime': '10:00', 'everyweek': 2,
             'preps': '', 'prep_short_name': '',
             'prep_id': 123, 'auditories_verbose': '', 'day': 3,
             'nt': 2, 'title': 'les_1', 'ngroup': 1, 'dend': datetime.date(2021, 1, 16)},
        ]

        expected = []

        result = convert_teachers_schedule(input_value)
        self.assertEqual(result, expected)

    if __name__ == '__main__':
        unittest.main()
