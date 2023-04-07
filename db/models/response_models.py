from datetime import date, timedelta

class LessonsTime:
    def __init__(self, id_66: int, para: str, begtime: str, endtime: str):
        self.lesson_id = id_66
        self.lesson_number = para
        self.begtime = begtime
        self.endtime = endtime

    def __dict__(self):
        return {
            'lesson_id': self.lesson_id,
            'lesson_number': self.lesson_number,
            'begtime': self.begtime,
            'endtime': self.endtime
        }


class Institute:
    def __init__(self, faculty_id: int, faculty_title: str):
        self.institute_id = faculty_id
        self.institute_title = faculty_title

    def __dict__(self):
        return {
            'institute_id': self.institute_id,
            'institute_title': self.institute_title
        }


class Group:
    def __init__(self, id_7: int, obozn: str, kurs: int, faculty_id: int):
        self.group_id = id_7
        self.name = obozn
        self.course = kurs
        self.institute_id = faculty_id

    def __dict__(self):
        return {
            'group_id': self.group_id,
            'name': self.name,
            'course': self.course,
            'institute_id': self.institute_id
        }


class Teacher:
    def __init__(self, id_61: int, preps: str, prep: str):
        self.teacher_id = id_61
        self.fullname = preps
        self.shortname = prep

    def __dict__(self):
        return {
            'teacher_id': self.teacher_id,
            'fullname': self.fullname,
            'shortname': self.shortname
        }


class Classroom:
    def __init__(self, id_60: int, obozn: str):
        self.classroom_id = id_60
        self.name = obozn

    def __dict__(self):
        return {
            'classroom_id': self.classroom_id,
            'name': self.name
        }


class Disciplines:
    def __init__(self, id: int, title: str, real_title: str):
        self.discipline_id = id
        self.title = title
        self.real_title = real_title

    def __dict__(self):
        return {
            'discipline_id': self.discipline_id,
            'title': self.title,
            'real_title': self.real_title
        }


class OtherDiscipline:
    def __init__(self, id: int, discipline_title: str, type: int, is_online: bool):
        self.other_discipline_id = id
        self.discipline_title = discipline_title
        self.is_online = is_online
        self.type = type

    def __dict__(self):
        return {
            'other_discipline_id': self.other_discipline_id,
            'discipline_title': self.discipline_title,
            'is_online': self.is_online,
            'type': self.type
        }


class Schedule:
    def __init__(self, id: int, groups: list, groups_verbose: str, teachers: list,
                 teachers_verbose: str, auditories: list, auditories_verbose: str, discipline: int,
                 discipline_verbose: str, meta_program_discipline_id: int, para: int, type: str, ngroup: int,
                 nt: int, dbeg: date, day: int, everyweek: int):
        self.schedule_id = id
        self.groups_ids = groups
        self.groups_verbose = groups_verbose
        self.teachers_ids = teachers
        self.teachers_verbose = teachers_verbose
        if auditories is not None:
            self.auditories_id = auditories[0] if any(auditories) else None
        else:
            self.auditories_id = None
        self.auditories_verbose = auditories_verbose
        self.discipline_id = discipline
        self.discipline_verbose = discipline_verbose
        self.other_discipline = meta_program_discipline_id
        self.lesson_id = para
        self.subgroup = ngroup
        self.lesson_type = nt
        self.schedule_type = type
        self.date = dbeg + timedelta(days=(day - 1) % 7)

    def __dict__(self):
        return {
            'schedule_id': self.schedule_id,
            'groups_ids': self.groups_ids,
            'groups_verbose': self.groups_verbose,
            'teachers_ids': self.teachers_ids,
            'teachers_verbose': self.teachers_verbose,
            'auditories_id': self.auditories_id,
            'auditories_verbose': self.auditories_verbose,
            'discipline_id': self.discipline_id,
            'discipline_verbose': self.discipline_verbose,
            'other_discipline': self.other_discipline,
            'lesson_id': self.lesson_id,
            'subgroup': self.subgroup,
            'lesson_type': self.lesson_type,
            'schedule_type': self.schedule_type,
            'date': self.date
        }
