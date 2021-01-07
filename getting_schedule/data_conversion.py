def convert_institutes(pg_institutes: list) -> list:
    """Преобразование формата институтов"""
    if not pg_institutes:
        raise ValueError('Данные не могут быть пустыми')
    result_data = [{'name': institute['fac']} for institute in pg_institutes]
    return result_data


def convert_groups(pg_groups: list) -> list:
    """Преобразование формата групп"""
    if not pg_groups:
        raise ValueError('Данные не могут быть пустыми')
    result_data = [{
        'name': group['obozn'],
        'course': f"{group['kurs']} курс",
        'institute': group['fac']
    } for group in pg_groups]

    return result_data
