from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model
from tabulate import tabulate
import pprint
from functools import reduce

pp = pprint.PrettyPrinter(indent=4)


status_map = {
    0: 'unknown',
    1: 'invalid model',
    2: 'feasible',
    3: 'infeasible',
    4: 'optimal'
}

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

position_values_index = [
    2, 3, 4, 5, 6, 7, 11, 8, 10, 9
]


def main(
        num_intervals,
        formation_positions_with_name,
        playing_time_level = 'equal',
        force_starting_bench=[],
        missing_players=[]
):
    # Data
    formation_positions = formation_positions_with_name[:-1]
    model = cp_model.CpModel()

    position_weights = {
        2: 1,
        3: 1,
        4: 1,
        5: 1,
        6: 1,
        7: 1,
        11: 1,
        8: 1,
        10: 1,
        9: 1,
    }

    player_number_values = [
      # [2, 3, 4, 5, 6, 7, 11,8,10, 9],      # 'Positions',
      #   [0, 0, 0, 0, 0, 0, 1, 0, 0, 1],  # 'Aras',
      #   [0, 0, 0, 0, 0, 1, 0, 0, 0, 1],  # 'Bilind',
      #   [0, 0, 1, 0, 0, 0, 1, 0, 1, 0],  # 'Brady',
      #   [0, 1, 0, 0, 0, 0, 1, 0, 0, 1],  # 'Emir',
      #   [0, 0, 1, 0, 0, 0, 0, 1, 1, 0],  # 'Henry',
      #   [1, 1, 1, 0, 1, 0, 0, 0, 0, 0],  # 'James',
      #   [0, 0, 0, 0, 0, 1, 0, 0, 0, 1],  # 'Leo',
      #   [1, 1, 0, 0, 0, 1, 1, 0, 0, 1],  # 'Liam',
      #   [1, 1, 0, 0, 0, 1, 0, 0, 1, 0],  # 'Oliver',
      #   [1, 1, 0, 0, 0, 1, 1, 0, 0, 0],  # 'Owen',
      #   [0, 0, 0, 0, 1, 0, 0, 1, 1, 1],  # 'Sam',

    # # [2, 3, 4, 5, 6, 7, 11,8,10, 9],      # 'Positions',
        [2, 2, 2, 2, 2, 4, 4, 3, 5, 5],  # 'Aras',
        [4, 4, 3, 3, 2, 4, 3, 2, 2, 3],  # 'Bilind',
        [3, 4, 3, 3, 3, 4, 5, 4, 3, 3],  # 'Brady',
        [3, 4, 3, 3, 3, 3, 3, 2, 2, 2],  # 'Emir',
        [3, 4, 3, 3, 4, 3, 4, 5, 5, 4],  # 'Henry',
        [4, 4, 5, 4, 0, 0, 0, 0, 0, 0],  # 'James',
        [4, 4, 3, 3, 4, 4, 4, 3, 4, 3],  # 'Leo',
        [2, 2, 1, 1, 1, 2, 2, 1, 1, 2],  # 'Liam',
        [2, 2, 2, 2, 2, 3, 3, 2, 3, 3],  # 'Oliver',
        [2, 2, 2, 2, 0, 0, 0, 0, 1, 1],  # 'Owen',
        [3, 3, 3, 3, 4, 4, 3, 4, 5, 5],  # 'Sam',


        #
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
    # position_skills = []
    players = []
    num_players = len(ordered_roster_names) - len(missing_players)
    num_positions = len(formation_positions)

    def i_j_to_player_value(i, j):
        player_name = players[i]
        player_name_values_idx = ordered_roster_names.index(player_name)
        player_values = player_number_values[player_name_values_idx]
        player_values_idx = position_values_index.index(formation_positions[j])
        return player_values[player_values_idx]

    for i in range(len(ordered_roster_names)):
        if ordered_roster_names[i] not in missing_players:
            players.append(ordered_roster_names[i])

    # Variables
    x = {}
    for k in range(num_intervals):

        # vars for every combo of player-position-interval
        for i in range(num_players):
            for j in range(num_positions):
                x[(i, j, k)] = model.NewBoolVar(f'x[({i},{j},{k})]')

        # Each on field position is assigned to exactly one player
        for j in range(num_positions):
            model.AddExactlyOne(x[(i, j, k)] for i in range(num_players))

        # Each player is assigned to 0 to 1 positions in total
        for i in range(num_players):
            model.AddAtMostOne(x[(i, j, k)] for j in range(num_positions))

    # force initial bench
    for i in range(num_players):
        for j in range(num_positions):
            if players[i] in force_starting_bench:
                model.Add(x[(i, j, 0)] == 0)
                model.Add(x[(i, j, num_intervals-1)] == 0)

    # Keep players in the same position if they remain on the field
    same_position_bonus = {}
    for k in range(num_intervals):
        for i in range(num_players):
            for j in range(num_positions):
                if k > 0 and k != int(num_intervals/2):
                    last_position = x[(i, j, k-1)]
                    next_position = x[(i, j, k)]
                    same_position_bonus[(i, j, k)] = model.NewBoolVar(f'p[({i},{j},{k})]')
                    model.AddMinEquality(
                        same_position_bonus[(i, j, k)],
                        [next_position, last_position]
                    )

    # avoid bench twice in a row
    for i in range(num_players):
        for k in range(num_intervals):
            if k > 0:
                last_on_field = [x[(i, j, k-1)] for j in range(num_positions)]
                next_on_field = [x[(i, j, k)] for j in range(num_positions)]
                model.Add((sum(last_on_field) + sum(next_on_field)) > 0)


    objective_terms = []

    # Set variables for playing time
    players_position_intervals = []
    for i in range(num_players):
        s = cp_model.LinearExpr.Sum([x[(i, j, k)] for j in range(num_positions) for k in range(num_intervals)])
        players_position_intervals.append(s)

    if playing_time_level != 'unequal':

        if playing_time_level == 'equal':
            equal_var = model.NewIntVar(0, num_intervals, 'equalVar')
            model.AddMaxEquality(equal_var, players_position_intervals)
            model.AddMinEquality(equal_var, players_position_intervals)

        if playing_time_level == 'almost_equal':
            min_equal_var = int(num_intervals*.75)
            max_equal_var = 6
            model.AddMinEquality(int(num_intervals * .75), players_position_intervals)

        if playing_time_level == 'feasible_equality':
            min_equal_var = model.NewIntVar(0, num_intervals, 'equalVar')
            model.AddMinEquality(min_equal_var, players_position_intervals)
            max_equal_var = model.NewIntVar(0, num_intervals, 'equalVar')
            model.AddMaxEquality(num_intervals - max_equal_var, players_position_intervals)
            model.Add((num_intervals - max_equal_var) - min_equal_var < 2)
            objective_terms.append(min_equal_var)
            objective_terms.append(max_equal_var)

    # Objective

    for k in range(num_intervals):
        for i in range(num_players):
            for j in range(num_positions):
                player_value = i_j_to_player_value(i, j)
                position_weight = position_weights[formation_positions[j]]
                objective_terms.append(player_value * position_weight * x[(i, j, k)])

    for k in range(num_intervals):
        for i in range(num_players):
            for j in range(num_positions):
                if k > 0 and k != int(num_intervals/2):
                    objective_terms.append(same_position_bonus[(i, j, k)])

    model.Maximize(sum(objective_terms))

    # Solve
    solver = cp_model.CpSolver()
    # solver.parameters.log_search_progress = True
    solver.parameters.num_search_workers = 6
    solver.parameters.max_time_in_seconds = 30
    status = solver.Solve(model)

    if status != cp_model.OPTIMAL and status != cp_model.FEASIBLE:
        return status

    # Get and transform solution
    full_game_by_player = {}
    full_game_by_position = {}
    total_game_value = 0

    # For every player
    positions_reserved_by_interval = {}
    for k in range(num_intervals):
        positions_reserved_by_interval[k] = []
    for i in range(num_players):
        player_name = players[i]
        # For every Interval
        for k in range(num_intervals):
            # For every position
            position_played = 0
            for j in range(num_positions):
                if solver.BooleanValue(x[(i, j, k)]):
                    if formation_positions[j] in positions_reserved_by_interval[k]:
                        position_played = f'{formation_positions[j]}_b'
                    else:
                        position_played = formation_positions[j]
                        positions_reserved_by_interval[k].append(formation_positions[j])
            if player_name not in full_game_by_player:
                full_game_by_player[player_name] = [position_played]
            else:
                full_game_by_player[player_name].append(position_played)
            if position_played != 0:
                player_value = i_j_to_player_value(i, j)
                total_game_value += player_value

    # Every interval
    for k in range(num_intervals):
        players_benched = []
        players_playing = []
        # Add on-field position for each player
        positions_reserved = []
        for i in range(num_players):
            player_name = players[i]
            for j in range(num_positions):
                position = formation_positions[j]
                position_name = position
                if solver.BooleanValue(x[(i, j, k)]):
                    if position in positions_reserved:
                        position_name = f'{position}b'
                    players_playing.append(player_name)
                    if position_name not in full_game_by_position:
                        full_game_by_position[position_name] = [player_name]
                    else:
                        full_game_by_position[position_name].append(player_name)
                    positions_reserved.append(position)

    # Add bench
        for player in players:
            if player not in players_playing:
                players_benched.append(player)
        for idx, player in enumerate(players_benched):
            position = f'Bench {idx}'
            if position not in full_game_by_position:
                full_game_by_position[position] = [player]
            else:
                full_game_by_position[position].append(player)

    table_position_data = []
    table_player_data = []
    for player in players:
        data = full_game_by_player[player]
        intervals_played = list(filter(lambda position: position != 0, data))
        data = [*data, len(intervals_played)]
        table_player_data.append([player, *data])
    formation_positions_with_bench = formation_positions + [f'Bench {i}' for i in range(num_players-num_positions)]
    positions_reserved = []
    for position in formation_positions_with_bench:
        position_name = position
        if position in positions_reserved:
            position_name = f'{position}b'
        table_position_data.append([position_name, *full_game_by_position[position_name]])
        positions_reserved.append(position)

    return total_game_value, table_player_data, table_position_data, formation_positions_with_name



def iterations():
    force_starting_bench = [
        'Bilind',
        'Owen',
        'Liam'
    ]
    missing_players = []
    formations = [
        [2, 3, 4, 7, 8, 11, 10, 9, '3-3-2'],
        # [4, 5, 6, 8, 10, 7, 9, 11, '2-3-3 (4-5)'],
        # [2, 3, 6, 8, 10, 7, 9, 11, '2-3-3 (2-3)'],
        # [2, 4, 6, 8, 10, 7, 9, 11, '2-3-3 (2-4)'],
        # [2, 4, 3, 6, 8, 7, 9, 11, '3-2-3 (6-8)'],
        # [2, 4, 3, 8, 10, 7, 9, 11, '3-2-3 (8-10)'],
        # [2, 4, 7, 6, 8, 11, 10, 9, '2-4-2 (2-4)'],
        [2, 3, 7, 6, 8, 11, 10, 9, '2-4-2 (2-3)'],
        # [4, 5, 7, 6, 8, 11, 10, 9, '2-4-2 (4-5)'],
        # [2, 4, 3, 6, 7, 10, 11, 9, '3-1-3-1 (6-10)'],
        # [2, 4, 3, 8, 7, 10, 11, 9, '3-1-3-1 (8-10)'],
    ]
    # 3 3 2
    # formation_positions = [2, 3, 4, 7, 8, 11, 10, 9]
    # 2 3 3
    # formation_positions = [4, 5, 6, 8, 10, 7, 9, 11]
    # formation_positions = [2, 4, 6, 8, 10, 7, 9, 11]
    # formation_positions = [2, 3, 6, 8, 10, 7, 9, 11]
    # 2 4 2
    # formation_positions = [2, 4, 7, 6, 8, 11, 10, 9]
    # formation_positions = [2, 3, 7, 6, 8, 11, 10, 9]
    # formation_positions = [4, 5, 7, 6, 8, 11, 10, 9]
    force_interval = False
    # playing_level_time = 'unequal'
    playing_level_time = 'feasible_equality'
    for num_intervals in range(2, 10000000):
        if (num_intervals%2 == 0):
            if not force_interval:
                result = main(num_intervals, formations[0], playing_level_time, force_starting_bench, missing_players)
            else:
                result = 'pass'
                num_intervals = force_interval
            if (isinstance(result, int)):
                print(f'Solution not found for {num_intervals} intervals: {status_map[result]}')
            else:
                print(f'Solution found for {num_intervals} intervals')
                best_score = 0
                best_result = ()
                all_formations = []
                for fidx, f in enumerate(formations):
                    result = main(num_intervals, f, playing_level_time, force_starting_bench, missing_players)
                    if isinstance(result, int):
                        print(f'Failure: {status_map[result]}')
                        exit()
                    print(f'{fidx}/{len(formations)}: Solution found for {f}')
                    (score,
                     table_player_data,
                     table_position_data,
                     best_formation
                     ) = result
                    all_formations.append([score/num_intervals, f[-1]])
                    if score > best_score:
                        best_score = score
                        best_result = (score,
                                       table_player_data,
                                       table_position_data,
                                       best_formation,
                                       )
                (score,
                 table_player_data,
                 table_position_data,
                 best_formation
                 ) = best_result
                print(f'Num Intervals: {num_intervals}')
                print(f'Best formation: {best_formation}')
                print(f'Score: {best_score/num_intervals}')
                print('')
                print('')
                interval_columns = [i+1 for i in range(num_intervals)] + ['Total']
                # table_player_data_totals =
                print(tabulate(table_player_data, headers=['Player', *interval_columns], tablefmt="fancy_grid"))
                print('')
                print('')
                print(tabulate(table_position_data, headers=['Position', *[i+1 for i in range(num_intervals)]], tablefmt="fancy_grid"))
                print('')
                print(f'All formation scores:')
                pp.pprint(sorted(all_formations, key=lambda x: (x[0]), reverse=True))
                exit()


if __name__ == '__main__':
    iterations()
