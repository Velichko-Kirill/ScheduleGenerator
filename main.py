from pathlib import Path
from deap import tools
from GeneticAlgorithm import GeneticAlgorithm, load_results_from_dat, save_results_to_dat, Config
from Entities import ScheduleConfig, MainData
from ExcelParser import ExcelParser
from Schedule import Schedule
from ScheduleExporter import ScheduleExporter

def main():
    data_path = Path().resolve() / "data" / "input_constraints.xlsx"
    parser = ExcelParser(data_path)
    parser.setup()

    # Schedule initialization (if you still need it)
    schedule = Schedule(parser.data)
    config = ScheduleConfig(
        daily_hours_limit=8,
        weekly_hours_limit=48,
        daily_difficult_hours_limit=5
    )
    data = MainData()
    data.set_schedule_config(config)

    # Genetic Algorithm setup
    algo = GeneticAlgorithm(config=Config())

    # Load results from DAT file or run the genetic algorithm
    population_selected = load_results_from_dat()

    if population_selected is None:
        population_selected = algo.run()
        save_results_to_dat(population_selected)

    best_individual = tools.selBest(population_selected, 1)[0]

    # Export the generated schedule
    exporter_ga = ScheduleExporter(best_individual, algo.encoding, parser.data)  
    exporter_ga.export_to_excel()



if __name__ == '__main__':
    main()