from ortools.sat.python import cp_model
from tabulate import tabulate
import pprint
import enum

pp = pprint.PrettyPrinter(indent=4)

class Playtime(enum.Enum):
    UNEQUAL = 0
    ALMOST_EQUAL = 1
    EQUAL = 2
    FEASIBLE = 3

status_map = {
    0: 'unknown',
    1: 'invalid model',
    2: 'feasible',
    3: 'infeasible',
    4: 'optimal'
}

left_footers = [
    'Aras',
    'Emir',
    'Henry',
    'Brady'
]

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
        formation_positions_data,
        playing_time_level = 'equal',
        force_starting_bench=[],
        missing_players=[],
        vary_positions=True,
        no_on_field_changes=True,
        no_long_bench=True,
):

    formation_positions = formation_positions_data[1:]
    model = cp_model.CpModel()
    player_number_values = [

        # Best guess on skill-level
        ['Position',    2,      3,      4,      5,      6,      7,      11,     8,      10,     9,      1],
        ['Aras',        3,      3.1,    3,      2,      2,      4,      4.1,    3,      5,      5,      0],
        ['Bilind',      4,      4,      3,      3,      2,      4,      3,      2,      2,      3,      0],
        ['Brady',       3,      4,      3,      3,      3,      4,      5,      4,      3,      3,      1],
        ['Emir',        3,      3.1,    3,      3,      3,      3,      3.1,    2,      2,      2,      1],
        ['Henry',       3,      4.1,    3,      3,      4,      3,      4.1,    5,      5,      4,      3],
        ['James',       4,      4,      5,      4,      0,      0,      0,      0,      0,      0,      0],
        ['Leo',         4,      4.1,    3,      3,      4,      4,      4,      3,      4,      3,      2],
        ['Liam',        2,      2,      1,      1,      1,      2,      2,      1,      1,      2,      0],
        ['Oliver',      2,      2,      2,      2,      2,      3,      3,      2,      3,      3,      3],
        ['Owen',        2,      2,      2,      2,      0,      0,      0,      0,      1,      1,      0],
        ['Sam',         3,      3,      3,      3,      4,      4,      3,      4,      5,      5,      2],
        ['Weight',      1,      1,      1,      1,      1,      1,      1,      1,      1,      1,      1]

        # Best guess on skill-level
        # ['Position',    2, 3, 4, 5, 6, 7,11, 8,10, 9, 1],
        # ['Aras',2.833333333,2.833333333,3,3,3,3.5,3.5,3.25,3.75,4, 0],
        # ['Bilind',3.333333333,3.333333333,3.25,3.25,3.25,3.5,3.5,3.25,3.25,3, 0],
        # ['Brady',3.5,3.5,3.75,3.75,3.5,3.5,3.5,3.5,3.75,3.75, 0],
        # ['Emir',2.833333333,2.833333333,3,3,2.75,3,3,3,3.25,3.5, 0],
        # ['Henry',3.333333333,3.333333333,3.75,3.75,4,3.75,3.75,4,4,3.5, 0],
        # ['James',3,3,3.25,3.25,3,2.75,2.75,3.25,2.75,2.75, 0],
        # ['Leo',3.666666667,3.666666667,3.5,3.5,3.75,4,4,3.75,4,3.25, 0],
        # ['Liam',2.833333333,2.833333333,2.75,2.75,2.75,2.5,2.5,2.5,2.5,2.25, 0],
        # ['Oliver',3.333333333,3.333333333,3.25,3.25,3.25,3.25,3.25,3.25,3.5,3.5, 100],
        # ['Owen',2.333333333,2.333333333,2,2,2.25,2,2,2,2.25,2.5, 0],
        # ['Sam',3.166666667,3.166666667,3.25,3.25,3.25,3.75,3.75,3.5,3.75,3.75, 100],
        # ['Weight',      1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

    ]
    players = [row[0] for idx, row in enumerate(player_number_values)
               if idx != 0
               and
               idx != len(player_number_values)-1
               and
               row[0] not in missing_players]
    values_idx_by_player = [row[0] for row in player_number_values]
    num_players = len(player_number_values) - len(missing_players) - 2
    num_positions = int(len(formation_positions)/2)
    formation_labels = [i for i in formation_positions if isinstance(i, str)]
    formation_numbers = [i for i in formation_positions if not isinstance(i, str)]
    number_to_player_value_idx = player_number_values[0][1:]

    def j_to_values_indexes(j):
        numbers = formation_numbers[j]
        return [number_to_player_value_idx.index(n) for n in numbers]

    def i_j_to_player_value(i, j):
        player_name = players[i]
        player_values_idx = values_idx_by_player.index(player_name)
        player_values = player_number_values[player_values_idx][1:]
        values_indexes = j_to_values_indexes(j)
        values_to_max = []
        for idx in values_indexes:
            value = player_values[idx]
            number = player_number_values[0][idx+1]
            if player_name in left_footers and number in [3, 7, 11]:
                value += .1
            values_to_max.append(value)
        return max(values_to_max)

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
    if no_on_field_changes:
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

    # Prevent a player from always playing the same position
    if vary_positions:
        sum_intervals = {}
        for i in range(num_players):
            n_intervals = model.NewIntVar(0,num_intervals, f'sum_intervals[{i}]')
            model.Add(n_intervals == sum(x[(i, j, k)] for k in range(num_intervals) for j in range(num_positions)))
            sum_intervals[i] = n_intervals

        for i in range(num_players):
            for j in range(num_positions):
                # Prevent player from playing the same position the entire game.
                model.Add(sum_intervals[i] > sum(x[(i, j, k)] for k in range(num_intervals)))

    objective_terms = []

    # avoid bench twice in a row
    if no_long_bench:
        for i in range(num_players):
            for k in range(num_intervals):
                if k > 0:
                    last_on_field = [x[(i, j, k-1)] for j in range(num_positions)]
                    next_on_field = [x[(i, j, k)] for j in range(num_positions)]
                    model.Add((sum(last_on_field) + sum(next_on_field)) > 0)

    # Set variables for playing time
    if playing_time_level != Playtime.UNEQUAL:



        # Get num intervals a player is allocated
        players_position_intervals = []
        for i in range(num_players):
            s = cp_model.LinearExpr.Sum([x[(i, j, k)] for j in range(num_positions) for k in range(num_intervals)])
            players_position_intervals.append(s)

        if playing_time_level == Playtime.EQUAL:
            equal_var = model.NewIntVar(0, num_intervals, 'equalVar')
            model.AddMaxEquality(equal_var, players_position_intervals)
            model.AddMinEquality(equal_var, players_position_intervals)

        if playing_time_level == Playtime.ALMOST_EQUAL:
            model.AddMinEquality(int(num_intervals * .75), players_position_intervals)

        if playing_time_level == Playtime.FEASIBLE:
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
                objective_terms.append(player_value * x[(i, j, k)])

    if no_on_field_changes:
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
    solver.parameters.max_time_in_seconds = 5
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
            position_played = ''
            for j in range(num_positions):
                if solver.BooleanValue(x[(i, j, k)]):
                    position_played = formation_labels[j]
            if player_name not in full_game_by_player:
                full_game_by_player[player_name] = [position_played]
            else:
                full_game_by_player[player_name].append(position_played)
            if position_played != '':
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
                position_name = formation_labels[j]
                if solver.BooleanValue(x[(i, j, k)]):
                    players_playing.append(player_name)
                    if position_name not in full_game_by_position:
                        full_game_by_position[position_name] = [player_name]
                    else:
                        full_game_by_position[position_name].append(player_name)

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
        intervals_played = list(filter(lambda position: position != '', data))
        data = [*data, len(intervals_played)]
        table_player_data.append([player, *data])
    formation_positions_with_bench = formation_labels + [f'Bench {i}' for i in range(num_players-num_positions)]
    for position_name in formation_positions_with_bench:
        table_position_data.append([position_name, *full_game_by_position[position_name]])

    return total_game_value, table_player_data, table_position_data, formation_positions_data



def iterations():
    force_starting_bench = []
    missing_players = ['Brady']
    vary_position = False
    force_interval = False
    min_intervals = 4
    no_on_field_changes = False
    no_long_bench = False
    playing_level_time = Playtime.FEASIBLE
    formations = [
        [
            '3-3-2',
            'GK', [1],
            'LD', [3],
            'CD', [4, 5],
            'RD', [2],
            'LM', [11],
            'CM', [6, 8, 10],
            'RM', [7],
            'S1', [9],
            'S2', [9],
        ],
        [
            '2-4-2',
            'GK', [1],
            'LD', [3, 4, 5],
            'RD', [2, 4, 5],
            'LM', [11],
            'CM1', [6, 8, 10],
            'CM2', [6, 8, 10],
            'RM', [7],
            'S1', [9, 10],
            'S2', [9, 10],
        ],
        [
            '2-3-3',
            'GK', [1],
            'LD', [3, 4, 5],
            'RD', [2, 4, 5],
            'LM', [11],
            'CM', [6, 8, 10],
            'RM', [7],
            'LF', [9, 10, 11],
            'CF', [9, 10],
            'RF', [9, 10, 7],
        ],
        [
            '3-2-3',
            'GK', [1],
            'LD', [3],
            'CD', [4, 5, 6],
            'RD', [2],
            'CM1', [6, 8],
            'CM2', [6, 8],
            'LF', [9, 10, 11],
            'CF', [9, 10],
            'RF', [9, 10, 7],3
        ],
        [
            '3-1-3-1',
            'GK', [1],
            'LD', [3],
            'CD', [4, 5, 6],
            'RD', [2],
            'CM_D', [6],
            'LM', [11],
            'CM', [8, 10],
            'RM', [7],
            'S', [9]
        ],
    ]

    for num_intervals in range(min_intervals, 10000000):
        if (num_intervals%2 == 0):
            if not force_interval:
                result = main(num_intervals,
                              formations[0],
                              playing_level_time,
                              force_starting_bench,
                              missing_players,
                              vary_position,
                              no_on_field_changes,
                              no_long_bench
                              )
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
                    result = main(num_intervals,
                                  f,
                                  playing_level_time,
                                  force_starting_bench,
                                  missing_players,
                                  vary_position,
                                  no_on_field_changes,
                                  no_long_bench
                                  )
                    if isinstance(result, int):
                        print(f'Failure: {status_map[result]}')
                        exit()
                    print(f'{fidx}/{len(formations)}: Solution found for {f}')
                    (score,
                     table_player_data,
                     table_position_data,
                     best_formation_data
                     ) = result
                    all_formations.append([score/num_intervals, f[0]])
                    if score > best_score:
                        best_score = score
                        best_result = (score,
                                       table_player_data,
                                       table_position_data,
                                       best_formation_data,
                                       )
                (score,
                 table_player_data,
                 table_position_data,
                 best_formation_data
                 ) = best_result
                print(f'Num Intervals: {num_intervals}')
                print(f'Best formation: {best_formation_data}')
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
