import statistics
from ortools.sat.python import cp_model
from tabulate import tabulate
import enum

class Playtime(enum.Enum):
    UNEQUAL = 0
    FEASIBLE = 1


class GameFormations:
    def __init__(self):
        self.formation_definitions = [
            [
                '3-3-2',
                'GK',   [1],
                'LD',    [3],
                'CD',    [4, 5],
                'RD',    [2],
                'LM',    [11],
                'CM',   [8],
                'RM',    [7],
                'LS',    [9],
                'RS',   [9],
            ],
            [
                '3-4-1',
                'GK',   [1],
                'LD',   [3],
                'CD',   [4, 5],
                'RD',   [2],
                'LM',   [11],
                'CM-L', [8],
                'CM-R', [8],
                'RM',   [7],
                'S',    [9],
            ],
            [
                '3-4-1-Diamond',
                'GK',   [1],
                'LD',   [3],
                'CD',   [4, 5],
                'RD',   [2],
                'LW',   [11],
                'CM-D', [6],
                'CM-O', [10],
                'RW',   [7],
                'S',    [9],
            ],
            [
                '3-2-3',
                'GK',   [1],
                'LD',   [3],
                'CD',   [4, 5],
                'RD',   [2],
                'CM-D', [6, 8],
                'CM-O', [10],
                'LF',   [11],
                'CF',   [10, 9],
                'RF',   [9],
            ],
            # [
            #     '4-3-1',
            #     'GK', [1],
            #     'LD', [3],
            #     'CLD', [3, 4, 5],
            #     'CRD', [2, 4, 5],
            #     'RD', [2],
            #     'LM', [11],
            #     'CM', [6, 8, 10],
            #     'RM', [7],
            #     'S', [9],
            # ],
            # [
            #     '2-4-2',
            #     'GK', [1],
            #     'LD', [3, 4, 5],
            #     'RD', [2, 4, 5],
            #     'LM', [11],
            #     'CM1', [6, 8, 10],
            #     'CM2', [6, 8, 10],
            #     'RM', [7],
            #     'LS', [9, 10],
            #     'RS', [9, 10],
            # ],
            # [
            #     '2-3-3',
            #     'GK', [1],
            #     'LD', [3, 4, 5],
            #     'RD', [2, 4, 5],
            #     'LM', [11],
            #     'CM', [6, 8, 10],
            #     'RM', [7],
            #     'LF', [9, 10, 11],
            #     'CF', [9, 10],
            #     'RF', [9, 10, 7],
            # ],
            # [
            #     '3-2-3',
            #     'GK', [1],
            #     'LD', [3],
            #     'CD', [4, 5, 6],
            #     'RD', [2],
            #     'CM1', [6, 8],
            #     'CM2', [6, 8],
            #     'LF', [9, 10, 11],
            #     'CF', [9, 10],
            #     'RF', [9, 10, 7],3
            # ],
            # [
            #     '3-1-3-1',
            #     'GK', [1],
            #     'LD', [3],
            #     'CD', [4, 5, 6],
            #     'RD', [2],
            #     'CM_D', [6],
            #     'LM', [11],
            #     'CM', [8, 10],
            #     'RM', [7],
            #     'S', [9]
            # ]
        ]

    def get_formation(self, name):
        for f in self.formation_definitions:
            if name == f[0]:
                return f[1:]

    def get_formation_names(self):
        return [f[0] for f in self.formation_definitions]


class GameRoster:
    def __init__(self,
                 missing_players,
                 ):

        self.missing_players = missing_players

        self.left_footers = [
            'Aras',
            'Emir',
        ]
        self.left_numbers = [3, 7, 11]
        self.left_foot_additive = 0

        self.player_values_table = [
            ['Position',    1,       2,      3,      4,      5,      6,      7,      11,     8,      10,     9],
            ['Aras',        0,       0,      0,      0,      0,      0,      6,      6,      3,      6,      6],
            ['Bilind',      0,       1,      1,      1,      1,      1,      3,      3,      1,      3,      3],
            ['Cole',        0,       0,      0,      0,      0,      0,      2,      2,      2,      2,      2],
            ['Emir',        0,       0,      0,      0,      0,      0,      4,      4,      4,      4,      4],
            ['Dominic',     0,       1,      1,      1,      1,      1,      1,      1,      1,      1,      1],
            ['Stephen',     0,       1,      1,      1,      1,      1,      1,      1,      1,      1,      1],
            ['Samuel',      0,       1,      1,      1,      1,      1,      3,      3,      0,      0,      0],
            ['James',       0,       0,      0,      0,      0,      5,      5,      5,      5,      3,      3],
            ['Leo',         0,       0,      0,      0,      0,      5,      6,      6,      6,      6,      6],
            ['Liam',        0,       2,      2,      1,      1,      1,      1,      1,      1,      1,      1],
            ['Oliver',      2,       0,      0,      0,      0,      0,      0,      0,      0,      0,      0],
            ['Owen',        0,       0,      0,      0,      0,      3,      3,      3,      3,      3,      3],
            ['Sam',         0,       0,      0,      0,      0,      0,      6,      6,      1,      6,      6],
        ]

    def get_player_max_value_by_numbers(self, player_name, player_numbers):
        return max(self.get_player_values_by_numbers(player_name, player_numbers))

    def get_player_values_by_numbers(self, player_name, player_numbers):
        values = []
        for n in player_numbers:
            values.append(self.get_player_value_by_number(player_name, n))
        return values

    def get_player_value_by_number(self, player_name, player_number):
        table_columns = self.player_values_table[0]
        player_number_index = table_columns.index(player_number)
        player_rows = self.player_values_table[1:]
        for row in player_rows:
            if row[0] == player_name:
                for idx, value in enumerate(row):
                    if idx == player_number_index:
                        if player_name in self.left_footers and player_number in self.left_numbers:
                            return value + self.left_foot_additive
                        else:
                            return value

    def get_player_max_value_by_numbers_idx(self, player_name, player_numbers_idx):
        return max(self.get_player_values_by_numbers_idx(player_name, player_numbers_idx))

    def get_player_values_by_numbers_idx(self, player_name, player_numbers_idx):
        values = []
        for i in player_numbers_idx:
            values.append(self.get_player_value_by_number_idx(player_name, i))
        return values

    def get_player_value_by_number_idx(self, player_name, player_number_idx):
        table_columns = self.player_values_table[0]
        table_number_columns = table_columns[1:]
        player_number = table_number_columns[player_number_idx]
        return self.get_player_value_by_number(player_name, player_number)

    def get_num_players(self):
        return len(self.get_player_names())

    def get_player_names(self):
        return [row[0] for row in self.player_values_table
                if row[0] != 'Position'
                and row[0] not in self.missing_players]


class GameSolution:
    def __init__(self, game_solver):
        self.game_solver: GameSolver = game_solver
        self.num_players = game_solver.num_players
        self.num_positions = game_solver.num_positions
        self.num_intervals = game_solver.num_intervals
        self.nums = [self.num_players, self.num_positions, self.num_intervals]
        self.players = game_solver.players
        self.ppi = game_solver.ppi
        self.ppi_solutions = {}

        self.full_game_by_player = {}
        self.full_game_by_position = {}
        self.table_player_data = []
        self.table_position_data = []
        self.interval_scores = [0 for i in range(self.num_intervals)]
        self.min_player_positions_values = {}

        self.positions_played_values = {}
        if game_solver.vary_positions:
            self.set_vary_positions_values()

        self.set_ppi_solutions()
        self.set_full_game_by_player()
        self.set_full_game_by_position()
        self.set_printable_table_data()
        self.set_interval_scores()

    def set_ppi_solutions(self):
        num_players, num_positions, num_intervals = self.nums
        solver = self.game_solver.solver
        for i in range(num_players):
            for k in range(num_intervals):
                for j in range(num_positions):
                    self.ppi_solutions[(i, j, k)] = solver.BooleanValue(self.ppi[(i, j, k)])

    def set_vary_positions_values(self):
        positions_played = self.game_solver.positions_played
        solver = self.game_solver.solver
        for i in range(self.num_players):
            for j in range(self.num_positions):
                self.positions_played_values[(i, j)] = solver.Value(positions_played[(i, j)])
        self.min_player_positions_values = [solver.Value(mpp) for mpp in self.game_solver.min_player_positions]

    def set_full_game_by_player(self):
        num_players, num_positions, num_intervals = self.nums
        players = self.players
        solver = self.game_solver.solver
        ppi = self.ppi
        full_game_by_player =  self.full_game_by_player
        formation_labels = self.game_solver.formation_labels

        for i in range(num_players):
            player_name = players[i]
            for k in range(num_intervals):
                position_played = ''
                for j in range(num_positions):
                    if solver.BooleanValue(ppi[(i, j, k)]):
                        position_played = formation_labels[j]
                if player_name not in full_game_by_player:
                    full_game_by_player[player_name] = [position_played]
                else:
                    full_game_by_player[player_name].append(position_played)

    def set_full_game_by_position(self):
        num_players, num_positions, num_intervals = self.nums
        players = self.players
        solver = self.game_solver.solver
        ppi = self.ppi
        full_game_by_position = self.full_game_by_position
        formation_labels = self.game_solver.formation_labels

        for k in range(num_intervals):
            players_benched = []
            players_playing = []
            # Add on-field position for each player
            for i in range(num_players):
                player_name = players[i]
                for j in range(num_positions):
                    position_name = formation_labels[j]
                    if solver.BooleanValue(self.ppi[(i, j, k)]):
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

    def set_printable_table_data(self):
        players = self.game_solver.players
        num_players, num_positions, num_intervals = self.game_solver.nums
        for player in players:
            data = self.full_game_by_player[player]
            intervals_played = list(filter(lambda position: position != '', data))
            data = [*data, len(intervals_played)]
            self.table_player_data.append([player, *data])
        formation_positions_with_bench = self.game_solver.formation_labels + \
                                         [f'Bench {i}' for i in range(num_players-num_positions)]
        for position_name in formation_positions_with_bench:
            self.table_position_data.append([position_name, *self.full_game_by_position[position_name]])

    def print_position_solution(self):
        num_players, num_positions, num_intervals = self.game_solver.nums
        print(tabulate(self.table_position_data, headers=[
            'Position',
            *[i+1 for i in range(num_intervals)]
        ], tablefmt="fancy_grid"))

    def print_player_solution(self):
        num_players, num_positions, num_intervals = self.game_solver.nums
        interval_columns = [i+1 for i in range(num_intervals)] + ['Total']
        print(tabulate(self.table_player_data, headers=['Player', *interval_columns], tablefmt="fancy_grid"))

    def set_interval_scores(self):
        num_players, num_positions, num_intervals = self.nums
        ppi_solutions = self.ppi_solutions

        for i in range(num_players):
            for k in range(num_intervals):
                for j in range(num_positions):
                    if ppi_solutions[(i, j, k)]:
                        self.interval_scores[k] += self.game_solver.i_j_to_player_value(i, j)

    def print_scores(self):
        print(f'Average Interval Score: {statistics.mean(self.interval_scores)/self.num_positions}')
        print(f'Min Interval Score: {min(self.interval_scores)/self.num_positions}')
        print(f'Max Interval Score: {max(self.interval_scores)/self.num_positions}')

    def print_min_player_position_values(self):
        print('Min Player Position Values:')
        for idx, mpp in enumerate(self.min_player_positions_values):
            player_name = self.game_solver.players[idx]
            print(f'{player_name}: {mpp}')

    def get_solution_score(self):
        return sum(self.interval_scores)


class GameSolver:
    def __init__(self,
                 num_intervals,
                 game_roster: GameRoster,
                 game_formations: GameFormations,
                 formation_name,
                 playing_time_level: Playtime,
                 force_starting_bench=[],
                 vary_positions=True,
                 no_on_field_changes=True,
                 no_long_bench=True,
                 one_goal_keeper=True,
                 ):
        self.status = 0
        self.num_intervals = num_intervals
        self.game_roster = game_roster
        self.playing_time_level = playing_time_level
        self.force_starting_bench = force_starting_bench
        self.vary_positions = vary_positions
        self.no_on_field_changes = no_on_field_changes
        self.no_long_bench = no_long_bench
        self.formation_name = formation_name

        self.status_map = {
            0: 'unknown',
            1: 'invalid model',
            2: 'feasible',
            3: 'infeasible',
            4: 'optimal'
        }

        self.formation_name = formation_name
        self.formation_positions = game_formations.get_formation(formation_name)
        self.player_number_values = game_roster.player_values_table
        self.players = game_roster.get_player_names()
        self.values_idx_by_player = [row[0] for row in self.player_number_values]
        self.num_players = len(self.players)
        self.num_positions = int(len(self.formation_positions) / 2)
        self.formation_labels = [i for i in self.formation_positions if isinstance(i, str)]
        self.formation_numbers = [i for i in self.formation_positions if not isinstance(i, str)]
        self.number_to_player_value_idx = self.player_number_values[0][1:]
        self.nums = [self.num_players, self.num_positions, self.num_intervals]

        self.model = cp_model.CpModel()
        self.ppi = {}  # Player-Position-Interval [{i, j, k}]
        self.same_position_bonus = {}
        self.same_position_bonus_multiplier = 10
        self.maximize_player_positions_multiplier = 5
        self.diff_var_bonus_multiplier = 10
        self.positions_played = {}
        self.objective_terms = []
        self.min_player_positions = []

        self.initialize_model_variables()
        self.set_basic_constraints()
        self.set_positions_played()

        if force_starting_bench:
            self.set_start_end_bench(force_starting_bench)
        if no_on_field_changes:
            self.reduce_on_field_changes()
        if vary_positions:
            self.maximize_player_positions()
        if no_long_bench:
            self.prevent_long_bench()
        if playing_time_level == Playtime.FEASIBLE:
            self.set_feasible_playing_time()

        if one_goal_keeper:
            self.one_goal_keeper()

        self.maximize_team_strength()

        self.solver = cp_model.CpSolver()
        self.set_solver_params(7, 5)

    def initialize_model_variables(self):
        # vars for every combo of player-position-interval
        for k in range(self.num_intervals):
            for i in range(self.num_players):
                for j in range(self.num_positions):
                    self.ppi[(i, j, k)] = self.model.NewBoolVar(f'x[({i},{j},{k})]')

    def set_basic_constraints(self):
        # Per interval
        for k in range(self.num_intervals):

            # Each on field position is assigned to exactly one player
            for j in range(self.num_positions):
                self.model.AddExactlyOne(self.ppi[(i, j, k)] for i in range(self.num_players))

            # Each player is assigned to 0 to 1 positions in total
            for i in range(self.num_players):
                self.model.AddAtMostOne(self.ppi[(i, j, k)] for j in range(self.num_positions))

    def maximize_team_strength(self):
        num_players, num_positions, num_intervals = self.nums
        for k in range(num_intervals):
            for i in range(num_players):
                for j in range(num_positions):
                    player_value = self.i_j_to_player_value(i, j)
                    self.objective_terms.append(player_value * self.ppi[(i, j, k)])

    def set_start_end_bench(self, bench_players):
        for i in range(self.num_players):
            for j in range(self.num_positions):
                if self.players[i] in bench_players:
                    self.model.Add(self.ppi[(i, j, 0)] == 0)
                    # self.model.Add(self.ppi[(i, j, self.num_intervals-1)] == 0)

    def prevent_long_bench(self):
        for i in range(self.num_players):
            for k in range(self.num_intervals):
                if k > 0:
                    last_on_field = [self.ppi[(i, j, k-1)] for j in range(self.num_positions)]
                    next_on_field = [self.ppi[(i, j, k)] for j in range(self.num_positions)]
                    self.model.Add((sum(last_on_field) + sum(next_on_field)) > 0)

    def set_feasible_playing_time(self):
        model = self.model
        num_players, num_positions, num_intervals = self.nums

        # Number of intervals each player is on the field for
        players_position_intervals = []
        for i in range(num_players):
            s = cp_model.LinearExpr.Sum([self.ppi[(i, j, k)]
                                         for j in range(num_positions)
                                         for k in range(num_intervals)])
            players_position_intervals.append(s)


        diff_var = model.NewIntVar(0, num_intervals, 'diff_var')
        lt_equal_var = model.NewIntVar(0, num_intervals, 'ltEqualVar')
        min_equal_var = model.NewIntVar(0, num_intervals, 'minEqualVar')
        model.AddMinEquality(min_equal_var, players_position_intervals)
        max_equal_var = model.NewIntVar(0, num_intervals, 'maxEqualVar')
        model.AddMaxEquality(num_intervals - max_equal_var, players_position_intervals)
        model.Add((num_intervals - max_equal_var) - min_equal_var < diff_var)
        self.objective_terms.append(diff_var * -1 * self.diff_var_bonus_multiplier)
        self.objective_terms.append(min_equal_var)
        self.objective_terms.append(max_equal_var)
        self.objective_terms.append(lt_equal_var)

    def set_positions_played(self):
        for i in range(self.num_players):
            for j in range(self.num_positions):
                self.positions_played[(i, j)] = self.model.NewIntVar(0, 1, f'positions_played_{i}_{j}')
                self.model.AddMaxEquality(self.positions_played[(i, j)],
                                          [self.ppi[(i, j, k)] for k in range(self.num_intervals)])

    def maximize_player_positions(self):
        num_players, num_positions, num_intervals = self.nums
        self.min_player_positions = [self.model.NewIntVar(0, num_positions, f'min_player_positions_{n}')
                                     for n in range(self.num_players)]
        for i in range(self.num_players):
            self.model.Add(
                sum([self.positions_played[(i, j)] for j in range(self.num_positions)])
                > self.min_player_positions[i])
        self.objective_terms.append(sum(self.min_player_positions) * self.maximize_player_positions_multiplier)

    def one_goal_keeper(self):
        # One goalkeeper per game
        self.model.Add(sum(self.positions_played[(i, 0)] for i in range(self.num_players)) == 1)

    def reduce_on_field_changes(self):
        for k in range(self.num_intervals):
            for i in range(self.num_players):
                for j in range(self.num_positions):
                    if k > 0 and k != int(self.num_intervals/2):
                        last_position = self.ppi[(i, j, k-1)]
                        next_position = self.ppi[(i, j, k)]
                        self.same_position_bonus[(i, j, k)] = self.model.NewBoolVar(f'p[({i},{j},{k})]')
                        self.model.AddMinEquality(
                            self.same_position_bonus[(i, j, k)],
                            [next_position, last_position]
                        )
                        self.objective_terms.append(
                            self.same_position_bonus[(i, j, k)] * self.same_position_bonus_multiplier
                        )

    def set_solver_params(self, workers, max_time):
        # solver.parameters.log_search_progress = True
        self.solver.parameters.num_search_workers = workers
        self.solver.parameters.max_time_in_seconds = max_time

    def solve(self):
        self.model.Maximize(sum(self.objective_terms))
        self.status = self.solver.Solve(self.model)

        ## Get all possible optimal solutions (rounded, of course)
        # obj_val = round(self.solver.ObjectiveValue())
        # obj_terms_val = sum(self.objective_terms)
        # self.model.Add(obj_terms_val == obj_val)
        # self.model.Proto().ClearField('objective')
        # self.solver.parameters.max_time_in_seconds = float('inf')
        # self.solver.parameters.enumerate_all_solutions = True
        # vals = []
        # for v in self.ppi.values():
        #     vals.append(v)
        # solution = cp_model.VarArraySolutionPrinter(vals)
        # self.status = self.solver.Solve(self.model, solution)

        if self.status != cp_model.OPTIMAL and self.status != cp_model.FEASIBLE:
            return self.status_map[self.status]
        else:
            return GameSolution(self)

    def j_to_number_indexes(self, j):
        numbers = self.formation_numbers[j]
        return [self.number_to_player_value_idx.index(n) for n in numbers]

    def i_j_to_player_value(self, i, j):
        player_name = self.players[i]
        number_indexes = self.j_to_number_indexes(j)
        return self.game_roster.get_player_max_value_by_numbers_idx(player_name, number_indexes)


def interval_formation_solution(game_roster, game_formations, num_intervals, formation_name):
    game_solver = GameSolver(
        num_intervals=num_intervals,
        game_roster=game_roster,
        formation_name=formation_name,
        game_formations=game_formations,
        vary_positions=False,
        no_long_bench=True,
        no_on_field_changes=True,
        playing_time_level=Playtime.FEASIBLE,
        force_starting_bench=[],
        one_goal_keeper=True,
    )
    game_solution = game_solver.solve()
    return game_solution


def interval_check(n, force_interval=False):
    if not force_interval:
        return n % 2 == 0
    else:
        return n == force_interval


def iterations():
    debug = False
    min_intervals = 4
    max_intervals = 12
    force_interval = False
    game_roster = GameRoster(missing_players=['Bilind'])
    game_formations = GameFormations()
    all_solutions = []
    best_solution = False
    best_solution_score = 0
    select_formations = game_formations.get_formation_names()
    # select_formations = game_formations.get_formation_names()[0:1]
    for f in select_formations:
        for n in range(min_intervals, max_intervals):
            if interval_check(n, force_interval): #  and 30 % (n/2) == 0
                game_solution = interval_formation_solution(
                    game_roster=game_roster,
                    game_formations=game_formations,
                    num_intervals=n,
                    formation_name=f
                )
                if isinstance(game_solution, GameSolution):
                    print(f'Solution found for {f} with {n} intervals')
                    all_solutions.append(game_solution)
                    score = game_solution.get_solution_score()
                    if score > best_solution_score:
                        best_solution_score = score
                        best_solution = game_solution
                else:
                    print(f'Solution not found for {f} with {n} intervals: {game_solution}')
            # else:
            #     print(f'Solution not found for {f} with {n} intervals: non-integer sub timing')
    if isinstance(best_solution, GameSolution):
        formation_name = best_solution.game_solver.formation_name
        num_intervals = best_solution.game_solver.num_intervals
        sub_every_n_mins = 30 / ((num_intervals / 2))
        best_solution.print_player_solution()
        best_solution.print_position_solution()
        best_solution.print_scores()
        print(f'Best solution: {formation_name} with {num_intervals} intervals')
        print(f'Sub every {sub_every_n_mins} minutes')
        if debug:
            print('')
            print('Debugging:')
            print('--')
            best_solution.print_min_player_position_values()
    else:
        print('No solutions found')

if __name__ == "__main__":
    iterations()
