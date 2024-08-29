import gc
import logging
import random
from itertools import product
from pathlib import Path
from pprint import pprint
from typing import Dict, List, Tuple

import numpy as np
from tqdm import tqdm
from deap import base, creator, tools
import matplotlib.pyplot as plt
from numpy.random import shuffle, choice

from models import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class GeneticAlgorithm:
    def __init__(self,
                 config: Config,
                 population_size=100,
                 crossover_prob=0.7,
                 mut_pb=0.2,
                 num_generations=20):
        self.config = config
        self.population_size = population_size
        self.crossover_prob = crossover_prob
        self.mut_pb = mut_pb
        self.num_generations = num_generations

        self.toolbox = base.Toolbox()
        self._setup_deap()

    def _setup_deap(self):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

        self.encoding_list = list(self.encoding.keys())

        # Register functions to create individuals and populations
        self.toolbox.register("attr_index", random.choice, self.encoding_list)  # Fixed this line
        # self.toolbox.register("individual", tools.initRepeat, creator.Individual,
        #                       self.toolbox.attr_index, n=48)  # 6 days, 8 hours => 6*8 = 48 slots
        self.toolbox.register("individual", lambda: creator.Individual(self.initialize_agent().flatten()))
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        # Register the evaluation function
        self.toolbox.register("evaluate", self.evaluate_schedule)

        # Register genetic operators
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

    @property
    def encoding(self) -> Dict[int, Tuple[int, int, int]]:
        """
        Maps id (int, primary) --> triple (teacher, subject, classroom) represents
        a single slot in the schedule.
        """
        # groups = list(range(self.config.n_groups))
        teachers = list(range(self.config.n_teachers))
        subjects = list(range(self.config.n_subjects))
        classrooms = list(range(self.config.n_classrooms))

        triples = list(product(*[teachers, subjects, classrooms]))

        return dict(zip(range(len(triples)), triples))

    def initialize_agent(self) -> np.ndarray:
        """Agent is a 6x8 (6 days, 8 hours)  matrix where each element is an index
        in encoding dictionary"""

        agent = np.full((self.config.n_days, self.config.n_hours), -1)

        available_slots = [(day, hour) for day in range(self.config.n_days)
                           for hour in range(self.config.n_hours)]
        shuffle(available_slots)

        # for day, hour in available_slots:
            # valid_triples = self.get_valid_triples(agent, day, hour)
            # if valid_triples:
            #     chosen_triple = choice(valid_triples)
            #     agent[day, hour] = chosen_triple

        return agent

    def get_valid_triples(self, agent: np.ndarray, day: int, hour: int) -> list:
        """
        Get a list of valid (subject, teacher, classroom) triples that can be placed
        in the given (day, hour) slot without violating constraints.
        """

        valid_triples = []
        for idx, (teacher, subject, classroom) in self.encoding.items():
            if not self.conflicts(agent, day, hour, teacher, classroom):
                valid_triples.append(idx)

        return valid_triples

    def conflicts(self, agent: np.ndarray, day: int, hour: int, teacher: int, classroom: int) -> bool:
        """
        Check if placing a (teacher, classroom) at (day, hour) conflicts with the current agent's state.
        """
        # print("Checking for conflicts...")

        for h in range(self.config.n_hours):
            if agent[day, h] != -1:  # Check only if the slot is filled
                existing_teacher, _, existing_classroom = self.encoding[agent[day, h]]
                if existing_teacher == teacher or existing_classroom == classroom:
                    return True

        return False

    def evaluate_schedule(self, individual):
        """
        Evaluate the fitness of an individual (schedule).
        The function returns a penalty score based on how many constraints are violated.
        """
        penalty = 0

        # Constraint 1: No teacher should be in two places at the same time
        teacher_slots, classroom_slots = {}, {}
        student_schedule = {day: [] for day in range(self.config.n_days)}

        for idx, triple_idx in enumerate(individual):
            day = idx // self.config.n_hours
            hour = idx % self.config.n_hours
            teacher, subject, classroom = self.encoding[triple_idx]
            student_schedule[day].append(hour)

            # Check if teacher is already teaching at this time
            if (day, hour) in teacher_slots.get(teacher, []):
                penalty += 10
            else:
                teacher_slots.setdefault(teacher, []).append((day, hour))

            # Check if classroom is already occupied at this time
            if (day, hour) in classroom_slots.get(classroom, []):
                penalty += 10
            else:
                classroom_slots.setdefault(classroom, []).append((day, hour))

        for day, hours in student_schedule.items():
            if len(hours) > 1:
                hours.sort()
                for i in range(1, len(hours)):
                    if hours[i] != hours[i - 1] + 1:
                        penalty += 5  # Penalty for each gap in the schedule

        logger.debug(f"Evaluated individual with penalty: {penalty}")

        return penalty,

    def generation_evolutionary_loop(self, population: List[List[int]]
                                     ) -> np.ndarray[np.ndarray[np.int8]]:
        offspring = self.toolbox.select(population, len(population))
        offspring = list(map(self.toolbox.clone, offspring))

        # Apply crossover and mutation
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < self.crossover_prob:
                self.toolbox.mate(child1, child2)

        for mutant in offspring:
            if random.random() < self.mut_pb:
                self.toolbox.mutate(mutant)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(self.toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Replace the old population with the new one
        population[:] = offspring

        # getting stats
        fits = [ind.fitness.values[0] for ind in population]
        length = len(population)
        mean = sum(fits) / length
        sum2 = sum(x * x for x in fits)
        std = abs(sum2 / length - mean ** 2) ** 0.5

        logger.info(f"Min: {min(fits)}")
        logger.info(f"Max: {max(fits)}")
        logger.info(f"Avg: {mean}")
        logger.info(f"Std: {std}")
        gc.collect()

        return population

    def run(self):
        next_genetarion = self.toolbox.population(n=self.population_size)
        fitnesses = map(self.toolbox.evaluate, next_genetarion)

        for ind, fit in zip(next_genetarion, fitnesses):
            ind.fitness.values = fit

        for _ in tqdm(range(self.num_generations)):
            next_genetarion = self.generation_evolutionary_loop(next_genetarion)

        return next_genetarion


if __name__ == "__main__":
    algo = GeneticAlgorithm(config=Config())
    population_selected = algo.run()
    pprint(population_selected)
