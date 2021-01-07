import postgre_storage
import data_conversion
from mongo_storage import MongodbService

mongo_storage = MongodbService().get_instance()


def main():
    # Институты
    # Получаем данные.
    pg_institutes = postgre_storage.get_institutes()
    # Преобразуем данные в нужный формат.
    mongo_institutes = sorted(data_conversion.convert_institutes(pg_institutes),
                              key=lambda x: x['name'])  # Сортируем массив
    # Сохраняем данные.
    mongo_storage.save_institutes(mongo_institutes)

    # Группы
    pg_groups = postgre_storage.get_groups()
    mongo_groups = sorted(data_conversion.convert_groups(pg_groups),
                          key=lambda x: x['name'])
    mongo_storage.save_groups(mongo_groups)  # Сохраняем группы

    # Курсы
    mongo_courses = sorted(data_conversion.convert_courses(mongo_groups),
                           key=lambda x: x['name'])
    mongo_storage.save_courses(mongo_courses)  # Сохраняем курсы

    # Расписание
    pg_schedule = postgre_storage.get_schedule()


if __name__ == '__main__':
    main()
