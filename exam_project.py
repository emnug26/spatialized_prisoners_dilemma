#!/usr/bin/python3

import sys
from collections import namedtuple
from random import randint
from time import time

WIDTH = int(sys.argv[1])
HEIGHT = int(sys.argv[2])


Strategy = namedtuple("Strategy", ["initial", "c_response", "d_response"])
class Cell:
    strategy: Strategy
    north: 'Cell'
    south: 'Cell'
    east: 'Cell'
    west: 'Cell'

    history_south: list[tuple[bool, bool]]
    history_east: list[tuple[bool, bool]]
    score: int
    def __init__(self, initial_strat):
        self.score = 0
        self.strategy = initial_strat
        self.history_east = []
        self.history_south = []

REWARDS = {
    (True, True): (3, 3),
    (True, False): (0, 5),
    (False, True): (5, 0),
    (False, False): (1, 1)
}
STRATEGIES = [
    Strategy(False, False, False),  #allways defect         black
    Strategy(False, False, True),   #suspicious_doormat     blue
    Strategy(False, True, False),   #suspicious_TFT         green
    Strategy(False, True, True),    #suspicious_pacifist    cyan
    Strategy(True, False, False),   #deceptive_defector     red
    Strategy(True, False, True),    #guillible_doormat      magenta
    Strategy(True, True, False),    #regular_TFT            yellow
    Strategy(True, True, True)      #regular_pacifist       white
]

def determine_new_strategy(player:Cell) -> Strategy:
    neighbors = (player.north, player.south, player.east, player.west)
    best = player
    for n in neighbors:
        if n.score > best.score:
            best = n
    return best.strategy


def color_block(cell: Cell) -> str:
    r = int(cell.strategy.initial) * 200
    g = int(cell.strategy.c_response) * 200
    b = int(cell.strategy.d_response) * 200

    # The next line requires some explanation:
    #    The string is surrounded by by '\033' - which executes an SGR (Select Graphic Rendition)
    #    '[' starts the sequence (it technically starts twice but '0m' just means reset to text mode)
    #    The data itself is a semicolon seperated value
    #    1st is the opcode - it means set the background color
    #    2nd is the mode - 2 means use 24-bit RGB truecolor
    #    and the rest are the color intensities. (0-255)
    #    m signifies the end of the control sequence. (it is required)
    #    the two spaces are necessary for the color to have something to 'paint'
    return f'\033[48;2;{r};{g};{b}m  \033[0m'

def same_state(a, b):
    return all(
        a[row][col].strategy == b[row][col].strategy
        for row in range(HEIGHT)
        for col in range(WIDTH)
    )

def print_graphic(matrix):
    for row in range(HEIGHT):
        line=''
        for col in range(WIDTH):
            colored_cell = color_block(matrix[row][col])
            line += colored_cell
        print(line)

def determine_outcome(player: Cell, opponent: Cell, first:bool) -> tuple[bool, bool]:
    if first:
        return (player.strategy.initial, opponent.strategy.initial)

    last_outcome = player.history_east[-1] if opponent == player.east else player.history_south[-1]
    player_cooperated, opponent_cooperated = last_outcome
    player_c = player.strategy.c_response if opponent_cooperated else player.strategy.d_response
    opponent_c = opponent.strategy.c_response if player_cooperated else opponent.strategy.d_response
    return (player_c, opponent_c)

def random_strat():
    return STRATEGIES[randint(0, len(STRATEGIES)-1)]

def set_neighbors(m: list[list[Cell]]):
    for row in range(HEIGHT):
        for col in range(WIDTH):
            cell = m[row][col]
            cell.south = m[(row + 1) % HEIGHT][col]
            cell.north = m[(row - 1) % HEIGHT][col]
            cell.east = m[row][(col + 1) % WIDTH]
            cell.west = m[row][(col - 1) % WIDTH]


# let's try to pre-compute the outcomes like on page 175:

all_possible_strat_cells = [Cell(s) for s in STRATEGIES]
score_matrix = [[0 for _ in range(8)] for _ in range(8)]

for i, player in enumerate(all_possible_strat_cells):
    for j, opponent in enumerate(all_possible_strat_cells):
        for game  in range(200):
            player.east = opponent # hack to make determine_outcome work
            outcome = determine_outcome(player, opponent, first=game == 0)
            rewards = REWARDS[outcome]
            player.history_east.append(outcome)
            score_matrix[i][j] += rewards[0]


width = max(len(str(x)) for row in score_matrix for x in row)
for row in score_matrix:
    #  :>{width} reserves space and right-aligns the element within that.
    print(" ".join(f"{matchup:>{width}}" for matchup in row))



matrix = [[Cell(random_strat()) for col in range(WIDTH)] for row in range(HEIGHT)]
matrix_copy = [[Cell(Strategy(matrix[row][col].strategy.initial, matrix[row][col].strategy.c_response, matrix[row][col].strategy.d_response), ) for col in range(WIDTH)] for row in range(HEIGHT)]
set_neighbors(matrix)
set_neighbors(matrix_copy)

for generation in range (20):
    start_game_1 = time()
    for game in range(200):
        for row in range(HEIGHT):
            for cell in matrix[row]:
                outcome_south = determine_outcome(cell, cell.south, first=game == 0)
                outcome_east = determine_outcome(cell, cell.east, first=game == 0)
                reward_south = REWARDS[outcome_south]
                reward_east = REWARDS[outcome_east]
                cell.score += reward_south[0]
                cell.score += reward_east[0]
                cell.south.score += reward_south[1]
                cell.east.score += reward_east[1]
                cell.history_south.append(outcome_south)
                cell.history_east.append(outcome_east)

    middle = time()

    for row in range(HEIGHT):
        for cell in matrix_copy[row]:
            strat_index = STRATEGIES.index(cell.strategy)
            south_strat_index = STRATEGIES.index(cell.south.strategy)
            east_strat_index = STRATEGIES.index(cell.east.strategy)

            cell.score += score_matrix[strat_index][south_strat_index]
            cell.south.score += score_matrix[south_strat_index][strat_index]
            cell.score += score_matrix[strat_index][east_strat_index]
            cell.east.score += score_matrix[east_strat_index][strat_index]

    end_game_2 = time()
    print_graphic(matrix)
    print()
    print_graphic(matrix_copy)
    print(generation)
    print(same_state(matrix,matrix_copy))
    print(f'game 1 took: {middle-start_game_1}s, game 2 took: {end_game_2-middle}s')

    new_strategies = [[determine_new_strategy(cell) for cell in row] for row in matrix]
    for row in range(HEIGHT):
        for col in range(WIDTH):
            cell = matrix[row][col]
            cell.history_east = []
            cell.history_south = []
            cell.strategy = new_strategies[row][col]
            cell.score = 0
    new_strategies = [[determine_new_strategy(cell) for cell in row] for row in matrix_copy]
    for row in range(HEIGHT):
        for col in range(WIDTH):
            cell = matrix_copy[row][col]
            cell.history_east = []
            cell.history_south = []
            cell.strategy = new_strategies[row][col]
            cell.score = 0
