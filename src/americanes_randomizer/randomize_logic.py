import random

import numpy as np
import pandas as pd

from americanes_randomizer.constants import Levels
from americanes_randomizer.db.models import Player


np.set_printoptions(formatter={"float": lambda x: f"{x:0.2f}"})


def distribute_americana(
    players: list[Player],
    probability_modification: float,
    americana_level: Levels,
) -> dict[str, list[str]]:
    players_df = pd.DataFrame([{"name": p.name, "level": p.level} for p in players])

    n_courts = int(len(players_df) / 4)
    standard_probability = 1 / n_courts

    level_numbers = {
        Levels.A: 5,
        Levels.B_PLUS: 4,
        Levels.B: 3,
        Levels.C_PLUS: 2,
        Levels.C: 1,
        Levels.D: 0,
    }
    distributions = {}
    americana_level_number = level_numbers[americana_level]

    print("PROBABILITIES")
    for level in level_numbers.keys():
        level_difference = (level_numbers[level] - americana_level_number) / 2
        distributions[level] = np.linspace(
            standard_probability + level_difference * probability_modification,
            standard_probability - level_difference * probability_modification,
            num=n_courts,
        )
        distributions[level] = np.array([np.maximum(p, 1e-15) for p in distributions[level]])
        print(f"\t{level}: {100 * distributions[level]}\n")

    players_per_court = {p: [] for p in range(n_courts)}
    open_courts = [p for p in range(n_courts)]
    full_courts = []

    players_df = players_df.sample(frac=1).reset_index(drop=True)

    for row_player in players_df.iterrows():
        player = row_player[1]
        assigned_court = random.choices(  # noqa: S311
            open_courts,
            k=1,
            weights=np.delete(distributions[player["level"]], full_courts),
        )[0]

        players_per_court[assigned_court].append(player["name"])

        if len(players_per_court[assigned_court]) >= 4:
            open_courts.remove(assigned_court)
            full_courts.append(assigned_court)

    return players_per_court
