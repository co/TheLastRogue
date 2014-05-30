from random import shuffle
import geometry
import rng

CENTER = (0, 0)

UP = (0, -1)
DOWN = (0, 1)
RIGHT = (1, 0)
LEFT = (-1, 0)

UP_LEFT = geometry.add_2d(UP, LEFT)
UP_RIGHT = geometry.add_2d(UP, RIGHT)
DOWN_RIGHT = geometry.add_2d(DOWN, RIGHT)
DOWN_LEFT = geometry.add_2d(DOWN, LEFT)

DIRECTIONS = [UP,
              UP_RIGHT,
              RIGHT,
              DOWN_RIGHT,
              DOWN,
              DOWN_LEFT,
              LEFT,
              UP_LEFT]


def get_shuffled_directions():
    random_directions = [UP, UP_RIGHT,
                         RIGHT, DOWN_RIGHT,
                         DOWN, DOWN_LEFT,
                         LEFT, UP_LEFT]
    shuffle(random_directions)
    return random_directions


AXIS_DIRECTIONS = [UP,
                   DOWN,
                   LEFT,
                   RIGHT]

DIAGONAL_DIRECTIONS = [UP_RIGHT,
                       DOWN_RIGHT,
                       DOWN_LEFT,
                       UP_LEFT]


def turn_back(direction):
    index = DIRECTIONS.index(direction)
    back_delta = len(DIRECTIONS) / 2
    back_index = (index + back_delta) % len(DIRECTIONS)
    return DIRECTIONS[back_index]


def turn_right(direction):
    index = DIRECTIONS.index(direction)
    turn_90_delta = len(DIRECTIONS) / 4
    right_index = (index + turn_90_delta) % len(DIRECTIONS)
    return DIRECTIONS[right_index]


def turn_left(direction):
    index = DIRECTIONS.index(direction)
    turn_90_delta = len(DIRECTIONS) / 4
    left_index = (index - turn_90_delta) % len(DIRECTIONS)
    return DIRECTIONS[left_index]


def turn_slight_right(direction):
    index = DIRECTIONS.index(direction)
    turn_45_delta = len(DIRECTIONS) / 8
    right_index = (index + turn_45_delta) % len(DIRECTIONS)
    return DIRECTIONS[right_index]


def turn_slight_left(direction):
    index = DIRECTIONS.index(direction)
    turn_45_delta = len(DIRECTIONS) / 8
    left_index = (index - turn_45_delta) % len(DIRECTIONS)
    return DIRECTIONS[left_index]


def turn_left_or_right(direction):
    if rng.coin_flip():
        return turn_left(direction)
    else:
        return turn_right(direction)
