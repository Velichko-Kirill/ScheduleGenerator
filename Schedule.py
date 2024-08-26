import random

class Schedule:
    def __init__(self, data):
        self.data = data  # Объект MainData, который содержит все данные
        self.schedule = {}  # Словарь для хранения расписания
        self.unplaced_subjects = {}  # Словарь для хранения предметов, которые не удалось разместить
        self.teacher_assignments = {}  # Словарь для хранения назначений преподавателей

    def generate_initial_schedule(self):
        print("Начало генерации начального расписания...")
        # Для каждой группы создаем расписание на основе данных в self.data
        for group_name, group in self.data.groups.items():
            print(f"Генерация расписания для группы {group_name}...")
            self.schedule[group_name] = self.generate_group_schedule(group)
        print("Генерация начального расписания завершена.")

        # Выводим информацию о предметах, которые не удалось разместить
        if self.unplaced_subjects:
            print("Предметы, которые не удалось разместить:")
            for group_name, subjects in self.unplaced_subjects.items():
                for subject_name in subjects:
                    print(f"  Группа: {group_name}, Предмет: {subject_name}")

    def generate_group_schedule(self, group):
        group_schedule = {day: [None] * 8 for day in range(6)}  # 6 дней, 8 слотов на день
        self.teacher_assignments[group.name] = {day: [None] * 8 for day in range(6)}  # Создаем словарь для назначений

        for subject_name, subject in group.subjects.items():
            try:
                remaining_hours = int(subject.weekly_hours)
            except ValueError:
                print(f"Ошибка: Некорректное количество часов для предмета {subject_name} в группе {group.name}. Пропускаем...")
                continue

            print(f"Распределение предмета {subject_name} ({remaining_hours} часов) для группы {group.name}...")

            attempts = 0
            while remaining_hours > 0:
                attempts += 1
                if attempts > 1000:
                    print(f"Ошибка: Слишком много попыток ({attempts}) для распределения предмета {subject_name} в группе {group.name}. Пропускаем...")
                    if group.name not in self.unplaced_subjects:
                        self.unplaced_subjects[group.name] = []
                    self.unplaced_subjects[group.name].append(subject_name)
                    break

                day = random.randint(0, 5)
                slot = random.randint(0, 7)

                print(f"Попытка распределения предмета {subject_name} в день {day + 1}, слот {slot + 1}...")

                if self.is_slot_available(group, group_schedule, subject_name, day, slot):
                    group_schedule[day][slot] = subject_name
                    teacher = self.get_teacher_for_subject(subject_name, group.name, day, slot)
                    self.teacher_assignments[group.name][day][slot] = teacher.name if teacher else "N/A"
                    remaining_hours -= 1
                    print(f"Предмет {subject_name} успешно распределен: день {day + 1}, слот {slot + 1}. Осталось часов: {remaining_hours}")
                else:
                    print(f"Не удалось распределить предмет {subject_name} в день {day + 1}, слот {slot + 1}. Попробуем снова...")

        return group_schedule


    def is_slot_available(self, group, group_schedule, subject_name, day, slot):
        # Получаем предмет
        subject = group.subjects[subject_name]

        # Проверка на наличие преподавателя
        teacher = self.get_teacher_for_subject(subject_name, group.name, day, slot)
        if teacher:
            if not self.is_teacher_available(teacher, day, slot):
                print(f"Преподаватель {teacher.name} занят в день {day + 1}, слот {slot + 1}.")
                return False
        else:
            print(f"Преподаватель для предмета {subject_name} не найден.")

        # Проверка на наличие свободного кабинета
        if not self.is_room_available(subject, day, slot):
            print(f"Нет доступного кабинета для предмета {subject_name} в день {day + 1}, слот {slot + 1}.")
            return False

        # Проверка на наличие окон
        if self.will_create_gap(group_schedule, day, slot):
            print(f"Распределение предмета {subject_name} в день {day + 1}, слот {slot + 1} создаст окно.")
            return False

        return True

    def is_room_available(self, subject, day, slot):
        # Проверяем, доступен ли кабинет с нужным оборудованием
        for room in self.data.rooms:
            if room.equipment == subject.equipment_requirement or subject.equipment_requirement is None:
                if self.is_room_free(room, day, slot):
                    return True
        return False

    def is_room_free(self, room, day, slot):
        # Проверяем, свободен ли кабинет в данный слот
        for group_name, group_schedule in self.schedule.items():
            if group_schedule[day][slot] == room.number:
                return False
        return True

    def will_create_gap(self, group_schedule, day, slot):
        # Проверка для нулевого слота (первое занятие)
        if slot == 0:
            # Урок может быть вставлен в нулевой слот, только если все остальные слоты на этот день свободны
            if all(s is None for s in group_schedule[day][1:]):
                return False
            else:
                return True

        # Проверка для промежуточных слотов
        if slot > 0 and slot < 7:
            # Проверяем все слоты слева от текущего
            for i in range(0, slot):
                if group_schedule[day][i] is None:
                    return True  # Если есть пустой слот слева, то это создаст окно

            # Проверка всех слотов справа от текущего
            for i in range(slot + 1, 8):
                if group_schedule[day][i] is not None:
                    return True  # Если есть заполненный слот справа, то это создаст окно

        # Если текущий слот - последний
        if slot == 7:
            # Проверяем все слоты слева от текущего
            for i in range(0, slot):
                if group_schedule[day][i] is None:
                    return True  # Если есть пустой слот слева, то это создаст окно

        return False

    def get_teacher_for_subject(self, subject_name, group_name, day, slot):
        available_teachers = []

        # Шаг 1: Ищем всех учителей, которые ведут нужный предмет
        for teacher in self.data.teachers.values():
            if subject_name in teacher.subjects_name:
                # Шаг 2: Проверяем, ведет ли этот учитель предмет в данной группе
                if group_name in teacher.available_groups_name:
                    # Шаг 3: Проверяем, свободен ли учитель в этот день и слот
                    if self.is_teacher_available(teacher, day, slot):
                        available_teachers.append(teacher)

        # Если есть несколько доступных учителей, выбираем случайного
        if available_teachers:
            return random.choice(available_teachers)
        else:
            return None

    def is_teacher_available(self, teacher, day, slot):
        # Проверяем, свободен ли преподаватель в этот день и слот
        for group_name, group_schedule in self.schedule.items():
            if group_name in teacher.available_groups_name:
                if group_schedule[day][slot] is not None:
                    return False
        return True

    def is_valid(self):
        # Проверка допустимости расписания (можно расширить для более детальных проверок)
        return True
