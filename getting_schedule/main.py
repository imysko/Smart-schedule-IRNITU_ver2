import postgre_storage
import data_conversion


def main():
    pg_institutes = postgre_storage.get_institutes()
    print(pg_institutes)
    mongo_institutes = data_conversion.convert_institutes(pg_institutes)
    print(mongo_institutes)

    pg_groups = postgre_storage.get_groups()
    print(pg_groups)
    mongo_groups = data_conversion.convert_groups(pg_groups)
    print(mongo_groups)


if __name__ == '__main__':
    main()
