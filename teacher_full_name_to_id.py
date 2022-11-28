from db.mongo_storage import MongodbServiceTG
from db.postgre_storage import get_teachers

teachers = get_teachers()
storage = MongodbServiceTG()
users = storage.get_data('users')
for user in users:
    storage.save_or_update_user(
        chat_id=user['chat_id'],
        group_id=user['group']
    )
users = storage.get_data('users')
for user in users:
    if user['course']:
        arr = list(filter(lambda teacher: teacher['fullname'] == user['group_id'], teachers))
        if len(arr) > 0:
            storage.save_or_update_user(
                chat_id=user['chat_id'],
                group_id=arr[0]['teacher_id']
            )
