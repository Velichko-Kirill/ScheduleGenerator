from dataclasses import dataclass
from typing import Tuple


@dataclass
class Config:
    n_groups: int = 10
    n_teachers: int = 23
    n_subjects: int = 14
    n_classrooms: int = 17
    n_days: int = 6
    n_hours: int = 8

    # n_days x n_hours
    agent_shape: Tuple[int, int, int] = (6, 8)
