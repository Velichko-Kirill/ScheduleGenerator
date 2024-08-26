class ScheduleConfig:
    def __init__(self, daily_hours_limit, weekly_hours_limit, daily_difficult_hours_limit):
        self.daily_hours_limit = daily_hours_limit
        self.weekly_hours_limit = weekly_hours_limit
        self.daily_difficult_hours_limit = daily_difficult_hours_limit


class Subject:
    def __init__(self, name, weekly_hours=0, is_difficult=False, equipment_requirement=None):
        self.name = name
        self.weekly_hours = weekly_hours
        self.is_difficult = is_difficult
        self.equipment_requirement = equipment_requirement
        self.day_constraints = [False] * 6  # 6 дней в неделе
        self.time_constraints = [False] * 8  # 8 слотов в день


class ClassGroup:
    def __init__(self, name):
        self.name = name
        self.subjects = {}  # Ключ - название предмета, значение - объект Subject

    def add_subject(self, subject):
        self.subjects[subject.name] = subject


class Teacher:
    def __init__(self, name):
        self.name = name
        self.subjects_name = []  # Список предметов, которые ведет преподаватель
        self.available_groups_name = []  # Список групп, в которых преподаватель преподает
        self.available_days = [True] * 6  # Доступность преподавателя по дням недели


class Room:
    def __init__(self, number, building, equipment, room_type=None):
        self.number = number
        self.building = building
        self.equipment = equipment
        self.room_type = room_type


class MainData:
    def __init__(self):
        self.schedule_config = None
        self.groups = {}  # Ключ - название группы, значение - объект ClassGroup
        self.teachers = {}  # Ключ - имя преподавателя, значение - объект Teacher
        self.rooms = []  # Список объектов Room


    def set_schedule_config(self, config):
        self.schedule_config = config

    def add_group(self, group):
        self.groups[group.name] = group

    def add_teacher(self, teacher):
        self.teachers[teacher.name] = teacher

    def add_room(self, room):
        self.rooms.append(room)

    def add_subject(self, subject):
        self.subjects[subject.name] = subject

    def add_subject_to_group(self, group_name, subject):
        if group_name in self.groups:
            self.groups[group_name].add_subject(subject)
        else:
            # Если группы нет, создаем ее и добавляем предмет
            group = ClassGroup(group_name)
            group.add_subject(subject)
            self.add_group(group)
