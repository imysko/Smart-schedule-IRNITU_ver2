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
