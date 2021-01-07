import unittest
from data_conversion import convert_institutes, convert_groups, convert_courses


class TestConversionMethods(unittest.TestCase):

    # Институты
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

    # Группы
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

    # Курсы
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
            {'name': '1 курс', 'institute': 'Институт архитектуры, строительства и дизайна'},
            {'name': '2 курс', 'institute': 'Институт высоких технологий'},
            {'name': '3 курс', 'institute': 'Институт недропользования'},
            {'name': '4 курс', 'institute': 'Институт высоких технологий'},
            {'name': '4 курс', 'institute': 'Институт недропользования', }
        ]
        result = convert_courses(input_value)
        self.assertEqual(result, expected)

    def test_convert_courses_emptyList_returnValueError(self):
        input_value = []
        with self.assertRaises(ValueError):
            convert_courses(input_value)


if __name__ == '__main__':
    unittest.main()
