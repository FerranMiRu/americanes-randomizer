import random

import numpy as np
import pandas as pd


np.set_printoptions(formatter={"float": lambda x: f"{x:0.2f}"})


def distribute_americana(
    players_file: str,
    probability_modification: float,
    americana_level: str,
) -> None:
    players_df = pd.read_csv(players_file, sep=";")
    n_courts = int(len(players_df) / 4)
    standard_probability = 1 / n_courts

    level_numbers = {"A+": 5, "A": 4, "B+": 3, "B": 2, "C+": 1, "C": 0}  # TO modify
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

    players_per_court = [[] for _ in range(n_courts)]
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

    print(players_per_court)
