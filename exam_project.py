#!/usr/bin/python3

import sys
from random import randint

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
    strategy: Strategy
    south: 'Cell'
    east: 'Cell'
    history_south: list[tuple[bool, bool]]
    history_east: list[tuple[bool, bool]]
    score: int
    def __init__(self, initial_strat):
        self.score = 0
        self.strategy = initial_strat
        self.history_east = []
        self.history_south = []

def transmit_strategy(player:Cell, opponent:Cell) -> Strategy:
    if (player.score > opponent.score):
        opponent.strategy = player.strategy
    elif (player.score < opponent.score):
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

def determine_outcome(player: Cell, opponent: Cell, first:bool) -> tuple[bool, bool]:
    if first:
        return (player.strategy.initial, opponent.strategy.initial)
    last_outcome: tuple
    if opponent == player.east:
        last_outcome = player.history_east[-1]
    else:
        last_outcome = player.history_south[-1]

    we_cooperated, they_cooperated = last_outcome

    will_cooperate = (
        player.strategy.c_response if they_cooperated
        else player.strategy.d_response
    )
    opponent_will_cooperate = (
        opponent.strategy.c_response if we_cooperated
        else opponent.strategy.d_response
    )
    return (will_cooperate, opponent_will_cooperate)


REWARDS = {
    (True, True): (3, 3),
    (True, False): (0, 5),
    (False, True): (5, 0),
    (False, False): (1, 1)
}
STRATEGIES = [
    Strategy(False, False, False), #allways defect black
    Strategy(False, False, True), #suspicious_doormat blue
    Strategy(False, True, False), #suspicious_TFT green
    Strategy(False, True, True), #suspicious_pacifist cyan
    Strategy(True, False, False), #deceptive_defector red
    Strategy(True, False, True), #guillible_doormat magenta
    Strategy(True, True, False), #regular_TFT yellow
    Strategy(True, True, True) #regular_pacifist white
]
def random_strat():
    return STRATEGIES[randint(0, len(STRATEGIES)-1)]
matrix = [[Cell(random_strat(), ) for col in range(WIDTH)] for row in range(HEIGHT)]

for row in range(HEIGHT):
    for col in range(WIDTH):
        cell = matrix[row][col]
        cell.south = matrix[(row + 1) % HEIGHT][col]
        cell.east = matrix[row][(col + 1) % WIDTH]

while (True):
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
    print_graphic(matrix)
    #print('')
    #input()
    for row in range(HEIGHT):
        for cell in matrix[row]:
            transmit_strategy(cell, cell.south)
            transmit_strategy(cell, cell.east)
