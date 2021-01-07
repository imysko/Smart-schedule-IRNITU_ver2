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
                              key=lambda x: x['name'])
    # Сохраняем данные.
    mongo_storage.save_institutes(mongo_institutes)

    # Группы
    pg_groups = postgre_storage.get_groups()
    mongo_groups = data_conversion.convert_groups(pg_groups)

    # Курсы
    mongo_courses = data_conversion.convert_courses(mongo_groups)
    mongo_storage.save_groups(mongo_groups)  # Сохраняем группы
    mongo_storage.save_courses(mongo_courses)  # Сохраняем курсы


if __name__ == '__main__':
    main()
