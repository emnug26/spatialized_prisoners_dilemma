import sys
from enum import Enum
from random import randint
from typing import NamedTuple


class Direction(Enum):
    EAST = 1
    SOUTH = 2
    WEST = 3
    NORTH = 4

class Strategy(NamedTuple): # inheriting from NamedTuple to avoid contructor
    initial: bool
    c_response: bool
    d_response: bool

class Cell:
    col: int
    row: int
    score: float
    strategy: Strategy
    # about the history dict:
    #   the value is the our previous actions, followed by the previous action of our opponent.
    #   the key is the direction of the neighor in question.
    #   the order of the value list is first-in-last_out.
    history: dict[Direction, list[tuple[bool, bool]]]

    def __init__(self, initial_strat, pos_row, pos_col):
        self.col = pos_col
        self.row = pos_row
        self.score = 0
        self.strategy = initial_strat
        self.history = { Direction.SOUTH:[], Direction.EAST:[] }

    # Cell in quotes because it's a forward reference. (since it's a self-reference it technically hasn't been defined yet.
    # The runtime doesn't care. The static type checker however, will make fuss if we reference it without the quotes.
    def get_neighbor(self, direction: Direction) -> 'Cell':
        match direction:
            case Direction.NORTH:
                return matrix[(self.row-1) % HEIGHT][self.col]
            case Direction.SOUTH:
                return matrix[(self.row+1) % HEIGHT][self.col]
            case Direction.EAST:
                return matrix[self.row][(self.col+1) % WIDTH]
            case Direction.WEST:
                return matrix[self.row][(self.col-1) % WIDTH]


'''
    Makes the cell with the lowest score assimilate a stronger strategy
    If both cells are equal in score, nothing happens.
'''


possible_strategies = [
    Strategy(False, False, False),  #allways defect
    Strategy(False, False, True),   #suspicious_doormat
    Strategy(False, True, False),   #suspicious_TFT
    Strategy(False, True, True),    #suspicious_pacifist
    Strategy(True, False, False),   #deceptive_defector
    Strategy(True, False, True),    #guillible_doormat
    Strategy(True, True, False),    #regular_TFT
    Strategy(True, True, True)      #regular_pacifist
]

def random_strat() -> Strategy|None:
    if len(possible_strategies) == 0:
        return None
    return possible_strategies[randint(0, len(possible_strategies) - 1)]

def transmit_strategy(c1:Cell, c2:Cell):
    if (c1.score > c2.score):
        c2.strategy = c1.strategy
    elif (c1.score < c2.score):
        c1.strategy = c2.strategy

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

def print_matrix():
    # prints the a coloured grid of cells
    # each cell color corresonds to the strategy which that cell would be using on the next iteration, when the grid was printed
    for row in range(HEIGHT):
        line=''
        for col in range(WIDTH):
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
def determine_outcome(player: Cell, direction: Direction, first) -> tuple[bool, bool]:
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

WIDTH = int(sys.argv[1])
HEIGHT = int(sys.argv[2])

matrix = [[Cell(random_strat(), row, col) for col in range(WIDTH)] for row in range(HEIGHT)]


# one tournament is comprised of an indeterminate number of games > len(possible_strategies)
# one is game comprised of 200 rounds
# each tournament results in a table of scores.
#
# after each game we check for each strategy that started, whether it was eliminated.
#   A strategy is concidered eliminated if none of the cells employs the strategy at the end of 200th round
#   The eliminated cell gets deleted from the list of possbible strategies (it does not enter the next game)
# at the beginning of the new game all scores are set to 0, and we generate a new matrix
while (True):
    for game in range(200):
        for row in range(HEIGHT):
            for cell in matrix[row]:
                southern_neighbor = cell.get_neighbor(Direction.SOUTH)
                eastern_neightbor = cell.get_neighbor(Direction.EAST)
                outcome_east = determine_outcome(cell, Direction.EAST, first=game == 0)
                outcome_south = determine_outcome(cell, Direction.SOUTH, first=game == 0)

                cell.history[Direction.SOUTH].append(outcome_south)
                cell.history[Direction.EAST].append(outcome_east)

                cell.score += get_reward(outcome_south)[0]
                cell.score += get_reward(outcome_east)[0]
                southern_neighbor.score += get_reward(outcome_south)[1]
                eastern_neightbor.score += get_reward(outcome_east)[1]
    print_matrix()
    input()
    for game in range(200):
        for row in range(HEIGHT):
            for cell in matrix[row]:
                southern_neighbor = cell.get_neighbor(Direction.SOUTH)
                eastern_neightbor = cell.get_neighbor(Direction.EAST)

                transmit_strategy(cell, southern_neighbor)
                transmit_strategy(cell, eastern_neightbor)




#pruneDeadStrategies()
#
# continue while len(possible_strategies) > 0
