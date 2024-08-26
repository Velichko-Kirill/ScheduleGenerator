import openpyxl
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment


class ScheduleExporter:
    def __init__(self, schedule, file_name="output_schedule.xlsx"):
        self.schedule = schedule
        self.file_name = file_name

    def export_to_excel(self):
        wb = Workbook()
        ws = wb.active
        ws.title = "Расписание"

        # Создание заголовков групп (строка 1)
        ws.cell(row=1, column=1, value="День/Слоты")
        for col, group_name in enumerate(self.schedule.schedule.keys(), start=2):
            ws.cell(row=1, column=col, value=group_name)

        # Установка ширины столбцов и форматирования
        for col in range(1, ws.max_column + 1):
            ws.column_dimensions[get_column_letter(col)].width = 16

        # Заполнение расписания
        current_row = 2
        for day in range(6):  # 6 дней
            day_name = f"День {day + 1}"
            ws.cell(row=current_row, column=1, value=day_name)
            current_row += 1

            for slot in range(8):  # 8 слотов
                ws.cell(row=current_row, column=1, value=f"Слот {slot + 1}")

                for col, group_name in enumerate(self.schedule.schedule.keys(), start=2):
                    group_schedule = self.schedule.schedule[group_name]
                    subject_name = group_schedule[day][slot]
                    if subject_name is not None:
                        teacher_name = self.schedule.teacher_assignments[group_name][day][slot]
                        cell = ws.cell(row=current_row, column=col, value=f"{subject_name}\n{teacher_name}")
                        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

                current_row += 1

            # Добавляем пустую строку между днями для удобства чтения
            current_row += 1

        # Автоподбор высоты строк
        for row in ws.iter_rows():
            for cell in row:
                if cell.value:
                    ws.row_dimensions[cell.row].height = None  # Автоподбор высоты строки

        # Сохранение файла
        wb.save(self.file_name)
        print(f"Расписание успешно экспортировано в файл {self.file_name}")
