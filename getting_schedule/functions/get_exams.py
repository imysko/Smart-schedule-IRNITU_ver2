from tools.storage import MongodbService

storage = MongodbService().get_instance()


def groups_exam(group):
    schedule = storage.get_schedule_exam(group=group)

    return schedule
