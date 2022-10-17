from datetime import datetime

from db import data_conversion, postgre_storage


def get_group_schedule(
        group_id: int,
        next_week: bool = False,
        selected_date: datetime = None) -> list:

    data_list = data_conversion.convert_schedule(
        pg_schedule=postgre_storage.get_schedule_by_group(group_id),
        next_week=next_week,
        selected_date=selected_date
    )

    data_list = data_conversion.schedule_group_by_teachers(data_list)

    return data_list


def get_teacher_schedule(
        teacher_id: int,
        next_week: bool = False,
        selected_date: datetime = None) -> list:

    data_list = data_conversion.convert_schedule(
        pg_schedule=postgre_storage.get_schedule_by_teacher(teacher_id),
        next_week=next_week,
        selected_date=selected_date
    )

    data_list = data_conversion.schedule_group_by_teachers(data_list)
    data_list = data_conversion.drop_current_teachers(data_list, teacher_id=teacher_id)
    data_list = data_conversion.schedule_group_by_groups(data_list)

    return data_list


def get_classroom_schedule(
        classroom_id: int,
        next_week: bool = False,
        selected_date: datetime = None) -> list:

    data_list = data_conversion.convert_schedule(
        pg_schedule=postgre_storage.get_schedule_by_classroom(classroom_id),
        next_week=next_week,
        selected_date=selected_date
    )

    data_list = data_conversion.schedule_group_by_teachers(data_list)
    data_list = data_conversion.schedule_group_by_groups(data_list)

    return data_list
