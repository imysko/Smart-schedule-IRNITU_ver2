from db.mongo_storage import MongodbServiceTG
from db.postgre_storage import get_teachers

teachers = get_teachers()
storage = MongodbServiceTG()
users = storage.get_data('users')
for user in users:
    if user['course']:
        storage.save_or_update_user(
            chat_id=user['chat_id'],
            group=list(filter(lambda teacher: teacher['fullname'] == user['group'], teachers))[0]['teacher_id']
        )
