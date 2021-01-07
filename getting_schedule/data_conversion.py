def convert_institutes(pg_data: list) -> list:
    """Преобразование формата институтов"""
    if not pg_data:
        raise ValueError('Данные не могут быть пустыми')
    result_data = [{'name': institute['fac']} for institute in pg_data]
    return result_data
