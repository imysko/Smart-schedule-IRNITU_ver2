from db.mongo_storage import MongodbServiceTG
from db.postgre_storage import get_teachers, get_groups


def main():
    teachers = get_teachers()
    groups = get_groups(is_active=False)

    storage = MongodbServiceTG()
    users = list(storage.get_data('users'))

    teachers_to_id = {i['fullname']: i['teacher_id'] for i in teachers}
    groups_to_id = {i['name']: i['group_id'] for i in groups}

    for user in users:
        if 'group' in user:
            storage.save_or_update_user(
                chat_id=user['chat_id'],
                teachers_ids=list(filter(None, [teachers_to_id.get(user['group'], None)])),
                groups_ids=list(filter(None, [groups_to_id.get(user['group'], None)])),
            )


if __name__ == '__main__':
    main()
