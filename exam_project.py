#!/usr/bin/python3

import sys
from random import randint

class Strategy:
    initial: bool
    c_response: bool
    d_response: bool
    def __init__(self, initial, c_response, d_response):
        self.initial = initial
        self.c_response = c_response
        self.d_response = d_response

class Cell:
    strategy: Strategy
    south: 'Cell'
    east: 'Cell'
    history: dict['Cell', list[bool]]
    scores: dict['Cell', int]
    def __init__(self, strat: Strategy):
        self.strategy = strat
        self.scores = {}
        self.history = {}

WIDTH = 64#int(sys.argv[1])
HEIGHT = 64#int(sys.argv[2])
REWARDS = {
    (True, True): (3, 3),
    (True, False): (0, 5),
    (False, True): (5, 0),
    (False, False): (1, 1)
}
STRATEGIES = [
    Strategy(False, False, False),    #allways defect       black
    Strategy(False, False, True),     #suspicious_doormat   blue
    Strategy(False, True, False),     #suspicious_TFT       green
    Strategy(False, True, True),      #suspicious_pacifist  cyan
    Strategy(True, False, False),     #deceptive_defector   red
    Strategy(True, False, True),      #guillible_doormat    magenta
    Strategy(True, True, False),      #regular_TFT          yellow
    Strategy(True, True, True)        #regular_pacifist     white
]

def transmit_strategy(player:Cell, opponent:Cell) -> Strategy:
    if (player.scores[opponent] > opponent.scores[player]):
        opponent.strategy = player.strategy
    elif (player.scores[opponent] < opponent.scores[player]):
        player.strategy = opponent.strategy
    return player.strategy

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

''' Determines which "quadrant" we land in (CC, CD, DC DD)
    Returns the outcome as a tuple
'''
def determine_outcome(player: Cell, opponent: Cell, first:bool) -> tuple[bool, bool]:
    if first:
        return (player.strategy.initial, opponent.strategy.initial)

    opponent_cooperated = player.history[opponent][-1]
    player_cooperated = opponent.history[player][-1]
    player_c = player.strategy.c_response if opponent_cooperated else player.strategy.d_response
    opponent_c = opponent.strategy.c_response if player_cooperated else opponent.strategy.d_response
    return (player_c, opponent_c)

def random_strategy() -> Strategy:
    return STRATEGIES[randint(0, len(STRATEGIES)-1)]

def set_neighbors(m: list[list[Cell]]):
    for row in range(HEIGHT):
        for col in range(WIDTH):
            cell = m[row][col]
            cell.south = m[(row + 1) % HEIGHT][col]
            cell.east = m[row][(col + 1) % WIDTH]
            reset_cell(cell)

def reset_cell(cell):
    cell.scores[cell.south] = 0
    cell.scores[cell.east] = 0
    cell.east.scores[cell] = 0
    cell.south.scores[cell] = 0
    cell.history[cell.south] = []
    cell.history[cell.east] = []
    cell.east.history[cell] = []
    cell.south.history[cell] = []

matrix = [[Cell(random_strategy()) for col in range(WIDTH)] for row in range(HEIGHT)]
matrix_copy = [[Cell(matrix[row][col].strategy, ) for col in range(WIDTH)] for row in range(HEIGHT)]
set_neighbors(matrix)
set_neighbors(matrix_copy)

print(
    [[cell.strategy for cell in row] for row in matrix]
    ==
    [[cell.strategy for cell in row] for row in matrix_copy]
)
for _ in range(10):
    for game in range(200):
        for row in range(HEIGHT):
            for cell in matrix[row]:
                outcome_south = determine_outcome(cell, cell.south, game == 0)
                outcome_east = determine_outcome(cell, cell.east, game == 0)
                # simulating 2 games played,
                # updating scores for both parties
                cell.scores[cell.south] += REWARDS[outcome_south][0]
                cell.scores[cell.east] += REWARDS[outcome_east][0]
                cell.south.scores[cell] += REWARDS[outcome_south][1]
                cell.east.scores[cell] += REWARDS[outcome_east][1]

                # updating history for both parties, each remembers what the other did
                cell.history[cell.south].append(outcome_south[1])
                cell.history[cell.east].append(outcome_east[1])
                cell.south.history[cell].append(outcome_south[0])
                cell.east.history[cell].append(outcome_east[0])


    #print_graphic(matrix)
    #print('')
    #input()
    for row in range(HEIGHT):
        for cell in matrix[row]:
            transmit_strategy(cell, cell.south)
            transmit_strategy(cell, cell.east)
    for row in range(HEIGHT):
        for cell in matrix[row]:
            reset_cell(cell)

    for game in range(4):
        for row in range(HEIGHT):
            for cell in matrix_copy[row]:
                outcome_south = determine_outcome(cell, cell.south, game == 0)
                outcome_east = determine_outcome(cell, cell.east, game == 0)
                # simulating 2 games played,
                # updating scores for both parties
                cell.scores[cell.south] += REWARDS[outcome_south][0]
                cell.scores[cell.east] += REWARDS[outcome_east][0]
                cell.south.scores[cell] += REWARDS[outcome_south][1]
                cell.east.scores[cell] += REWARDS[outcome_east][1]

                # updating history for both parties, each remembers what the other did
                cell.history[cell.south].append(outcome_south[1])
                cell.history[cell.east].append(outcome_east[1])
                cell.south.history[cell].append(outcome_south[0])
                cell.east.history[cell].append(outcome_east[0])

    for row in range(HEIGHT):
        for cell in matrix_copy[row]:
            cell.strategy = transmit_strategy(cell, cell.south)
            cell.strategy = transmit_strategy(cell, cell.east)
    for row in range(HEIGHT):
        for cell in matrix_copy[row]:
            reset_cell(cell)


test_output ='200 rnds eq 4 rnds '
test_output += str(
    [[cell.strategy for cell in row] for row in matrix]
    ==
    [[cell.strategy for cell in row] for row in matrix_copy]
)
print(test_output)
print_graphic(matrix)
print('\n\n\n')
print_graphic(matrix_copy)
