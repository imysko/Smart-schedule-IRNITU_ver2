import unittest
from data_conversion import convert_institutes


class TestConversionMethods(unittest.TestCase):

    def test_convert_institutes_oneDictInList(self):
        input_value = [{'id_5': 664, 'fac': 'Аспирантура'}]
        expected = [{'name': 'Аспирантура'}]
        result = convert_institutes(input_value)
        self.assertEqual(result, expected)

    def test_convert_institutes_aFewDictInList(self):
        input_value = [
            {'id_5': 1, 'fac': 'Институт авиамашиностроения и транспорта'},
            {'id_5': 680, 'fac': 'Институт заочно-вечернего обучения'}
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



if __name__ == '__main__':
    unittest.main()
