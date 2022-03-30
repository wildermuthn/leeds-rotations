from ortools.linear_solver import pywraplp

ordered_roster_names = [
    'Aras',
    'Bilind',
    'Brady',
    'Emir',
    'Henry',
    'James',
    'Leo',
    'Liam',
    'Oliver',
    'Owen',
    'Sam',
]

ordered_player_numbers = [
    2, 3, 4, 5, 6, 7, 11, 8, 10, 9
]

def main():
    # Data
    roster_position_values = [
        # #    [2, 3, 4, 5, 6, 7, 11,8,10, 9],      # 'Positions',
        [2, 2, 2, 2, 3, 4, 3, 3, 4, 5],      # 'Aras',
        [3, 3, 2, 2, 2, 3, 3, 2, 3, 3],      # 'Bilind',
        [2, 2, 3, 3, 4, 3, 3, 4, 4, 3],      # 'Brady',
        [3, 3, 2, 2, 3, 2, 2, 2, 2, 3],      # 'Emir',
        [3, 3, 4, 4, 4, 3, 3, 5, 4, 4],      # 'Henry',
        [4, 4, 5, 5, 4, 2, 2, 2, 2, 2],      # 'James',
        [4, 4, 3, 3, 3, 4, 4, 3, 3, 4],      # 'Leo',
        [2, 2, 1, 1, 2, 3, 3, 1, 2, 2],      # 'Liam',
        [2, 2, 2, 2, 3, 3, 3, 3, 3, 3],      # 'Oliver',
        [2, 2, 2, 2, 1, 1, 1, 1, 2, 2],      # 'Owen',
        [3, 3, 3, 3, 3, 3, 3, 4, 5, 5],      # 'Sam',

        # [3, 3, 3, 3, 3.25, 3.75, 3.75, 3.25, 3.75, 3.75],
        # [3.333333333, 3.333333333, 3.5, 3.5, 3.25, 3.25, 3.25, 3.25, 3.25, 3.25],
        # [3.333333333, 3.333333333, 3.5, 3.5, 3.25, 3.25, 3.25, 3.5, 3.5, 3.75],
        # [3, 3, 3.25, 3.25, 3, 2.75, 2.75, 3.25, 3.25, 3.25],
        # [3.5, 3.5, 4, 4, 3.5, 3.75, 3.75, 4.25, 4, 4],
        # [3.5, 3.5, 4, 4, 3.75, 3.25, 3.25, 4, 3.5, 3.25],
        # [3.666666667, 3.666666667, 3.75, 3.75, 3.75, 3.75, 3.75, 4, 3.75, 3],
        # [2.833333333, 2.833333333, 2.75, 2.75, 2.75, 2.75, 2.75, 2.5, 2.75, 2.75],
        # [3.333333333, 3.333333333, 3.25, 3.25, 3.25, 3.5, 3.5, 3, 3.5, 3.5],
        # [2.5, 2.5, 2.25, 2.25, 2.5, 2.5, 2.5, 2.5, 2.75, 3],
        # [3.333333333, 3.333333333, 3.5, 3.5, 3.75, 3.5, 3.5, 3.5, 3.75, 3.5],


    ]
    force_to_bench = []
    on_field = []
    # 3 3 2
    formations_positions = [2, 3, 4, 7, 8, 11, 10, 9]
    # 2 3 3
    # formations_positions = [4, 5, 6, 8, 10, 7, 9, 11]
    # 2 4 2
    formations_positions = [4, 5, 7, 6, 8, 11, 10, 9]

    position_skills = []
    players = []
    formation_position_index = []
    # For each player's positional values
    for i in range(len(roster_position_values)):
        # As long as the player is not on the bnech
        if ordered_roster_names[i] not in force_to_bench:
            current_player_position_values = roster_position_values[i]
            filtered_position_values = []
            players.append(ordered_roster_names[i])
            for position_index in range(len(current_player_position_values)):
                if ordered_player_numbers[position_index] in formations_positions:
                    filtered_position_values.append(current_player_position_values[position_index])
                    if len(formation_position_index) < len(formations_positions):
                        formation_position_index.append(ordered_player_numbers[position_index])
            position_skills.append(filtered_position_values)

    num_players = len(position_skills)
    num_positions = len(position_skills[0])
    num_intervals = 2

    # Solver
    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver('GLOP')

    # Variables
    # x[i, j] is an array of 0-1 variables, which will be 1
    # if worker i is assigned to task j.
    x = {}
    for k in range(num_intervals):
        for i in range(num_players):
            for j in range(num_positions):
                x[i, j, k] = solver.IntVar(0, 1, '')

    # Constraints
    # Each worker is assigned to at most 1 task.
    for k in range(num_intervals):
        for i in range(num_players):
            solver.Add(solver.Sum([x[i, j, k] for j in range(num_positions)]) <= 1)

    # Each task is assigned to exactly one worker.
    for k in range(num_intervals):
        for j in range(num_positions):
            solver.Add(solver.Sum([x[i, j, k] for i in range(num_players)]) == 1)

    # Player gets at least 1 interval
    t = {}
    for i in range(num_players):
        for j in range(num_positions):
            t[i] = solver.Sum([x[i, j, k] for k in range(num_intervals)])
            solver.Add( t[i] >= 0)

    # Objective
    objective_terms = []
    for k in range(num_intervals):
        for i in range(num_players):
            for j in range(num_positions):
                objective_terms.append(position_skills[i][j] * x[i, j, k])

    for k in t:
        objective_terms.append(t[k])

    solver.Maximize(solver.Sum(objective_terms))
    # solver.Maximize(t)

    # Solve
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        print(f'Success')
    else:
        print('No solution found.')
        print(status)
        exit()

    # Print solution.

    for k in range(num_intervals):
        print(f'Total Value = {solver.Objective().Value()}\n')
        players_by_position = {}
        players_benched = []
        players_playing = []
        print(f'Interval: {k}')
        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            for i in range(num_players):
                for j in range(num_positions):
                    # print(i,j, x[i, j, k].solution_value())
                    if x[i, j, k].solution_value() > 0:
                        players_playing.append(players[i])
                        players_by_position[formation_position_index[j]] = players[i]

        for name in players:
            if name not in players_playing:
                players_benched.append(name)

        for benched in players_benched:
            print(f'{benched} is on bench')

        print("")

        for i in formations_positions:
            print(f'{i}: {players_by_position[i]}')

        print("")
        print("")


if __name__ == '__main__':
    main()
