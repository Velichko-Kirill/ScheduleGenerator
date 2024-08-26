from pathlib import Path

from Entities import ScheduleConfig, MainData
from ExcelParser import ExcelParser
from Schedule import Schedule
from ScheduleExporter import ScheduleExporter


def main():
    data_path = Path().resolve() / "data" / "input_constraints.xlsx"
    parser = ExcelParser(data_path)
    parser.setup()

    schedule = Schedule(parser.data)
    config = ScheduleConfig(
        daily_hours_limit=8,
        weekly_hours_limit=48,
        daily_difficult_hours_limit=5
    )
    data = MainData()
    data.set_schedule_config(config)

    # Экспортируем расписание в Excel
    # exporter = ScheduleExporter(schedule)
    # exporter.export_to_excel()


if __name__ == '__main__':
    main()
