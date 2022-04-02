from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model
from tabulate import tabulate
import pprint
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

ordered_player_numbers = [
    2, 3, 4, 5, 6, 7, 11, 8, 10, 9
]

def main(num_intervals, formation_positions, playing_time_level = 'equal'):
    # Data
    model = cp_model.CpModel()

    roster_position_values = [
      # [2, 3, 4, 5, 6, 7, 11,8,10, 9],      # 'Positions',
        [3, 3, 3, 3, 3, 3, 4, 3, 4, 5],  # 'Aras',
        [3, 3, 2, 2, 2, 2, 3, 2, 2, 3],  # 'Bilind',
        [4, 4, 4, 4, 4, 5, 5, 4, 4, 4],  # 'Brady',
        [3, 3, 3, 3, 3, 3, 2, 2, 2, 3],  # 'Emir',
        [4, 4, 5, 5, 4, 4, 4, 5, 4, 5],  # 'Henry',
        [4, 4, 4, 4, 4, 3, 3, 3, 2, 2],  # 'James',
        [5, 4, 4, 4, 4, 5, 4, 4, 4, 4],  # 'Leo',
        [2, 2, 1, 1, 1, 2, 2, 1, 1, 2],  # 'Liam',
        [3, 3, 2, 2, 3, 4, 4, 3, 3, 3],  # 'Oliver',
        [2, 2, 2, 2, 1, 1, 1, 1, 2, 2],  # 'Owen',
        [4, 4, 4, 4, 3, 5, 5, 4, 5, 5],  # 'Sam',

    ]
    force_to_bench = []

    position_skills = []
    players = []
    formation_position_index = []
    # For each player's positional values
    for i in range(len(roster_position_values)):
        # As long as the player is not on the bench
        if ordered_roster_names[i] not in force_to_bench:
            current_player_position_values = roster_position_values[i]
            filtered_position_values = []
            players.append(ordered_roster_names[i])
            for position_index in range(len(current_player_position_values)):
                if ordered_player_numbers[position_index] in formation_positions:
                    filtered_position_values.append(current_player_position_values[position_index])
                    if len(formation_position_index) < len(formation_positions):
                        formation_position_index.append(ordered_player_numbers[position_index])
            position_skills.append(filtered_position_values)

    num_players = len(position_skills)
    num_positions = len(position_skills[0])

    # num_intervals = 24

    # Solver
    # Create the mip solver with the SCIP backend.

    # Variables
    x = {}  # x[(player_id)(position_id)(interval)]  # position_id can be re-used instead of going with a tensor, by going from 0-7, then 8-15.
    for k in range(num_intervals):

        # vars for every combo of player-position-interval
        for i in range(num_players):
            for j in range(num_positions):
                x[(i, j, k)] = model.NewBoolVar(f'x[({i},{j},{k})]')

        # Each on field position is assigned to exactly one player
        for j in range(num_positions):
            all_players_for_one_position = [x[(i, j, k)] for i in range(num_players)]
            model.AddExactlyOne(all_players_for_one_position)

        # Each player is assigned to 0 to 1 positions in total
        for i in range(num_players):
            model.AddAtMostOne(x[(i, j, k)] for j in range(num_positions))

    # # Keep players in the same position if they remain on the field
    # for k in range(num_intervals):
    #     for i in range(num_players):
    #         for j in range(num_positions):
    #             if (k > 0):
    #                 last_position = x[(i, j, k-1)]
    #                 next_position = x[(i, j, k)]
    #                 model.AddBoolAnd(next_position, last_position).OnlyEnforceIf(next_position)

    # Set variables for playing time
    players_position_intervals = []
    for i in range(num_players):
        s = cp_model.LinearExpr.Sum([x[(i, j, k)] for j in range(num_positions) for k in range(num_intervals)])
        players_position_intervals.append(s)

    if playing_time_level == 'equal':
        equal_var = model.NewIntVar(0, 10000000, 'equalVar')
        model.AddMaxEquality(equal_var, players_position_intervals)
        model.AddMinEquality(equal_var, players_position_intervals)

    if playing_time_level == 'almost_equal':
        model.AddMinEquality(int(num_intervals * .75), players_position_intervals)

    if playing_time_level == 'feasible_equality':
        equal_var = model.NewIntVar(0, 10000000, 'equalVar')
        model.AddMinEquality(equal_var, players_position_intervals)

    # Objective
    objective_terms = []
    for k in range(num_intervals):
        for i in range(num_players):
            for j in range(num_positions):
                objective_terms.append(position_skills[i][j] * x[(i, j, k)])
    model.Maximize(sum(objective_terms))

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status != cp_model.OPTIMAL and status != cp_model.FEASIBLE:
        return status

    # Get and transform solution
    full_game_by_player = {}
    full_game_by_position = {}
    total_game_value = 0

    # For every player
    for i in range(num_players):
        player_name = players[i]
        # For every Interval
        for k in range(num_intervals):
            # For every position
            position_played = 0
            for j in range(num_positions):
                if solver.BooleanValue(x[(i, j, k)]):
                    position_played = formation_position_index[j]
            if player_name not in full_game_by_player:
                full_game_by_player[player_name] = [position_played]
            else:
                full_game_by_player[player_name].append(position_played)
            if position_played != 0:
                player_value = position_skills[i][j]
                total_game_value += player_value

    # Every interval
    for k in range(num_intervals):
        players_benched = []
        players_playing = []
        # Add on-field position for each player
        for i in range(num_players):
            player_name = players[i]
            for j in range(num_positions):
                position = formation_position_index[j]
                if solver.BooleanValue(x[(i, j, k)]):
                    players_playing.append(player_name)
                    if position not in full_game_by_position:
                        full_game_by_position[position] = [player_name]
                    else:
                        full_game_by_position[position].append(player_name)
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
    for position in formation_positions_with_bench:
        table_position_data.append([position, *full_game_by_position[position]])
    return total_game_value, table_player_data, table_position_data


def iterations():
    formations = [
        [2, 3, 4, 7, 8, 11, 10, 9, '3-3-2-standard'],
        [2, 3, 4, 7, 6, 8, 11, 9, '3-4-1'],
        [4, 5, 6, 8, 10, 7, 9, 11, '2-3-3-center-backs'],
        [2, 4, 6, 8, 10, 7, 9, 11, '2-3-3-mixed-backs'],
        [2, 3, 6, 8, 10, 7, 9, 11, '2-3-3-wing-backs'],
        [2, 4, 7, 6, 8, 11, 10, 9, '2-4-2-mixed-backs'],
        [2, 3, 7, 6, 8, 11, 10, 9, '2-4-2-wing-backs'],
        [4, 5, 7, 6, 8, 11, 10, 9, '2-4-2-center-backs'],
        [2, 3, 4, 5, 7, 8, 11, 9, '4-3-2-striker'],
        [2, 3, 4, 5, 7, 8, 11, 10, '4-3-2-fwd-mid'],
        [2, 3, 4, 5, 6, 8, 10, 9, '4-3-2-mid-heavy'],
        [2, 4, 3, 6, 7, 8, 11, 9, '3-1-3-1-striker'],
        [2, 4, 3, 6, 7, 8, 11, 10, '3-1-3-1-fwd-mid'],
    ]
    # 3 3 2
    # formations_positions = [2, 3, 4, 7, 8, 11, 10, 9]
    # 2 3 3
    # formations_positions = [4, 5, 6, 8, 10, 7, 9, 11]
    # formations_positions = [2, 4, 6, 8, 10, 7, 9, 11]
    # formations_positions = [2, 3, 6, 8, 10, 7, 9, 11]
    # 2 4 2
    # formations_positions = [2, 4, 7, 6, 8, 11, 10, 9]
    # formations_positions = [2, 3, 7, 6, 8, 11, 10, 9]
    # formations_positions = [4, 5, 7, 6, 8, 11, 10, 9]
    force_interval = False
    playing_level_time = 'equal'
    for num_intervals in range(6, 10000000):
        if not force_interval:
            result = main(num_intervals, formations[0][:-1], playing_level_time)
        else:
            result = 'pass'
            num_intervals = force_interval
        if (isinstance(result, int)):
            print(f'Solution not found for {num_intervals} intervals: {status_map[result]}')
        else:
            print(f'Solution found for {num_intervals} intervals')
            best_score = 0
            best_formation = []
            all_formations = []
            for f in formations:
                result = main(num_intervals, f[:-1], playing_level_time)
                if isinstance(result, int):
                    print(f'Failure: {status_map[result]}')
                    exit()
                score, table_player_data, table_position_data = result
                all_formations.append([score, f[-1]])
                if score > best_score:
                    best_score = score
                    best_formation = f
            print(f'Num Intervals: {num_intervals}')
            print(f'Best formation: {best_formation}')
            print(f'Score: {best_score}')
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




# for j in range(num_positions):
#     if solver.BooleanValue(x[(i, j, k)]):
#         player_assignments.append([k, players[i], formation_position_index[j]])
#         players_playing.append(players[i])
#         players_by_position[formation_position_index[j]] = players[i]
#         lineup_value += position_skills[i][j]
#         if players[i] in player_time:
#             player_time[players[i]] += 1
#         else:
#             player_time[players[i]] = 1
#         if players[i] in full_game_player_positions:
#             full_game_player_positions[players[i]].append(formation_position_index[j])
#         else:
#             full_game_player_positions[players[i]] = [formation_position_index[j]]
#     else:
#         if players[i] in full_game_player_positions:
#             full_game_player_positions[players[i]].append(0)
#         else:
#             full_game_player_positions[players[i]] = [0]
