# todo: implement logic to change strategy
#
# understand the magic string in the color_block function


import sys
from random import randint

from collections import namedtuple


class Strategy:
    initial: bool
    d_response: bool
    c_response: bool
    def __init__(self, i, c, d):
        self.initial = i
        self.c_response = c
        self.d_response = d
    def tuple(self):
        return (self.initial, self.d_response, self.c_response)

class Cell:
    col:int
    row:int
    score : int
    strategy : Strategy
    # about the history dict:
    #   the value is the our previous strategies, followed by the previous strtegy of our opponent.
    #   the key is the direction of the neighor in question.
    #   the order of the value list is first-in-last_out.
    history : dict[str, list[tuple[bool, bool]]]

    def __init__(self, initial_strat, pos_row, pos_col):
        self.col = pos_col
        self.row = pos_row
        self.score = 0
        self.strategy = initial_strat
        self.history = { 'south':[], 'east':[] }

    # Cell in quotes because it's a forward reference. (since it's a self-reference it technically hasn't been defined yet.
    # The runtime doesn't care. The static type checker however, will make fuss if we reference it without the quotes.
    def get_neighbor(self, direction:str) -> 'Cell':
        match direction:
            case 'north':
                return matrix[(self.row-1) % height][self.col]
            case 'south':
                return matrix[(self.row+1) % height][self.col]
            case 'east':
                return matrix[self.row][(self.col+1) % width]
            case 'west':
                return matrix[self.row][(self.col-1) % width]
            case _:
                raise TypeError('direction argument invalid')

def random_strat() -> Strategy:
    return Strategy(bool(randint(0,1)), bool(randint(0,1)), bool(randint(0,1)))

def color_block(cell : Cell) -> str:
    r = int(cell.strategy.initial) * 255
    g = int(cell.strategy.c_response) * 255
    b = int(cell.strategy.d_response) * 255

    # The next line requires some explanation:
    #    The string is surrounded by by '\033' - which executes an SGR (Select Graphic Rendition)
    #    '[' starts the sequence (it technically starts twice but '0m' just means reset to text mode)
    #    The data itself is a semicolon seperated value
    #    1st is the opcode - it means set the background color
    #    2nd is the mode - 2 means use 24-bit RGB truecolor
    #    and the rest are the color intensities.
    #    m signifies the end of the control sequence. (it is required)
    #    the two spaces are necessary for the color to have something to "paint"
    return f'\033[48;2;{r};{g};{b}m  \033[0m'

def print_matrix():
    # prints the a coloured grid of cells
    # each cell color corresonds to the strategy which that cell would be using on the next iteration, when the grid was printed
    for row in range(height):
        line=''
        for col in range(width):
            colored_cell = color_block(matrix[row][col])
            line += colored_cell
        print(line)

def get_reward(outcome: tuple[bool, bool]) -> tuple[int, int]:
    match outcome:
        case (True, True):
            return (3, 3)
        case (True, False):
            return (0, 5)
        case (False, True):
            return (5, 0)
        case (False, False):
            return (1, 1)

'''
    Determines what two strategies will be used for a given pair of neighbors in a given round
'''
def determine_outcome(player:Cell, direction:str, first=False) -> tuple[bool, bool]:
    opponent = player.get_neighbor(direction)
    if first:
        return (player.strategy.initial, opponent.strategy.initial)
    outcome_hist = player.history[direction]
    we_cooperated, they_cooperated = outcome_hist[len(outcome_hist)-1]

    will_cooperate = (
        player.strategy.c_response if they_cooperated
        else player.strategy.d_response
    )
    opponent_will_cooperate = (
        opponent.strategy.c_response if we_cooperated
        else opponent.strategy.d_response
    )
    return (will_cooperate, opponent_will_cooperate)

width = int(sys.argv[1])
height = int(sys.argv[2])

matrix = [[Cell(random_strat(), row, col) for col in range(width)] for row in range(height)]

for n in range(200):
    for row in range(height):
        for col in range(width):
            cell = matrix[row][col]
            southern_neighbor = matrix[(row+1) % height][col]
            eastern_neightbor = matrix[row][(col+1) % width]
            outcome_east = determine_outcome(cell, 'east', n == 0)
            outcome_south = determine_outcome(cell, 'south', n == 0)

            #update histories for 2 games played
            cell.history['south'].append(outcome_south)
            cell.history['east'].append(outcome_east)

            #update scores for 2 games played
            cell.score += get_reward(outcome_south)[0]
            cell.score += get_reward(outcome_east)[0]
            southern_neighbor.score += get_reward(outcome_south)[1]
            eastern_neightbor.score += get_reward(outcome_east)[1]

print_matrix()
