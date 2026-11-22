#!/usr/bin/python3

import sys
from random import randint
from time import time

WIDTH = int(sys.argv[1])
HEIGHT = int(sys.argv[2])

class Strategy:
    initial: bool
    c_response: bool
    d_response: bool
    def __init__(self, initial, c_response, d_response):
        self.initial = initial
        self.c_response = c_response
        self.d_response = d_response

class Cell:
    score: int
    strategy: Strategy
    south: 'Cell'
    east: 'Cell'
    north: 'Cell'
    west: 'Cell'
    history_south: list[tuple[bool, bool]]
    history_east: list[tuple[bool, bool]]
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
    best = [player]
    for n in neighbors:
        if n.score > best[0].score:
            best = [n]
        elif n.score == best[0].score:
            best.append(n)

    return best[randint(0, len(best)-1)].strategy

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

matrix = [[Cell(random_strat(), ) for col in range(WIDTH)] for row in range(HEIGHT)]
generation = 0

# populate the neighbors after all cells are initalize
# (otherwise we will reference objects which don't exist yet)
for row in range(HEIGHT):
    for col in range(WIDTH):
        cell = matrix[row][col]
        cell.south = matrix[(row + 1) % HEIGHT][col]
        cell.north = matrix[(row - 1) % HEIGHT][col]
        cell.east = matrix[row][(col + 1) % WIDTH]
        cell.west = matrix[row][(col - 1) % WIDTH]

while (True):
    # main simulation loop
    start = time()
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

    generation += 1
    print_graphic(matrix)


    # we generate a matrix of new strategies in order to propagate them simultaneously
    # if we propagate them in place, we will not get the correct results
    new_strategies = [[determine_new_strategy(cell) for cell in row] for row in matrix]
    for row in range(HEIGHT):
        for col in range(WIDTH):
            cell = matrix[row][col]
            cell.history_east = []
            cell.history_south = []
            cell.strategy = new_strategies[row][col]
            cell.score = 0
    end = time()
    print(f'gen:{generation} took {round(end-start, 2)}s to calc ')
