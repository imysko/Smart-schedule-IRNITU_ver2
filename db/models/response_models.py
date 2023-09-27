from datetime import timedelta

from db.models.postgres_models import Vacpara, RealGroup, Prepod, Auditorie, DisciplineDB, \
    ScheduleMetaprogramDiscipline, \
    ScheduleV2, QueryDB


class LessonsTime:
    def __init__(self, vacpara: Vacpara):
        self.lesson_id = vacpara.id_66
        self.lesson_number = vacpara.para
        self.begtime = vacpara.begtime
        self.endtime = vacpara.endtime

    def dict(self):
        return {
            'lesson_id': self.lesson_id,
            'lesson_number': self.lesson_number,
            'begtime': self.begtime,
            'endtime': self.endtime
        }


class Institute:
    def __init__(self, real_group: RealGroup):
        self.institute_id = real_group.faculty_id
        self.institute_title = real_group.faculty_title

    def dict(self):
        return {
            'institute_id': self.institute_id,
            'institute_title': self.institute_title
        }


class Group:
    def __init__(self, real_group: RealGroup):
        self.group_id = real_group.id_7
        self.name = real_group.obozn
        self.course = real_group.kurs
        self.institute_id = real_group.faculty_id
        self.is_active = real_group.is_active

    def dict(self):
        return {
            'group_id': self.group_id,
            'name': self.name,
            'course': self.course,
            'institute_id': self.institute_id,
            'is_active': self.is_active
        }


class Teacher:
    def __init__(self, prepod: Prepod):
        self.teacher_id = prepod.id_61
        self.fullname = prepod.preps
        self.shortname = prepod.prep

    def dict(self):
        return {
            'teacher_id': self.teacher_id,
            'fullname': self.fullname,
            'shortname': self.shortname
        }


class Classroom:
    def __init__(self, auditorie: Auditorie):
        self.classroom_id = auditorie.id_60
        self.name = auditorie.obozn

    def dict(self):
        return {
            'classroom_id': self.classroom_id,
            'name': self.name
        }


class Discipline:
    def __init__(self, discipline_db: DisciplineDB):
        self.discipline_id = discipline_db.id
        self.title = discipline_db.title
        self.real_title = discipline_db.real_title

    def dict(self):
        return {
            'discipline_id': self.discipline_id,
            'title': self.title,
            'real_title': self.real_title
        }


class OtherDiscipline:
    def __init__(self, schedule_metaprogram_discipline: ScheduleMetaprogramDiscipline):
        self.other_discipline_id = schedule_metaprogram_discipline.id
        self.discipline_title = schedule_metaprogram_discipline.discipline_title
        self.is_online = schedule_metaprogram_discipline.is_online
        self.type = schedule_metaprogram_discipline.type
        self.is_active = schedule_metaprogram_discipline.is_active
        self.project_active = schedule_metaprogram_discipline.project_active

    def dict(self):
        return {
            'other_discipline_id': self.other_discipline_id,
            'discipline_title': self.discipline_title,
            'is_online': self.is_online,
            'type': self.type,
            'is_active': self.is_active,
            'project_active': self.project_active
        }


class Query:
    def __init__(self, query: QueryDB):
        self.query_id = query.id
        self.description = query.description

    def dict(self):
        return {
            'query_id': self.query_id,
            'description': self.description
        }


class Schedule:
    def __init__(self, schedule_v2: ScheduleV2, vacpara: Vacpara = None, groups: list[RealGroup] = [],
                 teachers: list[Prepod] = []):
        self.schedule_id = schedule_v2.id
        self.groups_ids = schedule_v2.groups
        self.groups_verbose = schedule_v2.groups_verbose
        self.teachers_ids = schedule_v2.teachers
        self.teachers_verbose = schedule_v2.teachers_verbose
        if schedule_v2.auditories is not None:
            self.auditories_id = schedule_v2.auditories[0] if any(schedule_v2.auditories) else None
        else:
            self.auditories_id = None
        self.auditories_verbose = schedule_v2.auditories_verbose
        self.discipline_id = schedule_v2.discipline
        self.discipline_verbose = schedule_v2.discipline_verbose
        self.other_discipline_id = schedule_v2.meta_program_discipline_id
        self.query_id = schedule_v2.query_id
        self.lesson_id = schedule_v2.para
        self.subgroup = schedule_v2.ngroup
        self.lesson_type = schedule_v2.nt
        self.schedule_type = schedule_v2.type
        self.date = schedule_v2.dbeg + timedelta(days=(schedule_v2.day - 1) % 7)

        self.lesson = LessonsTime(vacpara)
        self.groups = [Group(g) for g in groups]
        self.teachers = [Teacher(t) for t in teachers]

    def dict(self):
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
            'other_discipline_id': self.other_discipline_id,
            'query_id': self.query_id,
            'lesson_id': self.lesson_id,
            'subgroup': self.subgroup,
            'lesson_type': self.lesson_type,
            'schedule_type': self.schedule_type,
            'date': self.date.isoformat()
        }
