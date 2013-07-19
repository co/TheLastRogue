import random
import monster
import geometry as geo
import logging


def place_piece_on_random_tile(piece, dungeon_level):
    positions = [(x, y) for x in range(dungeon_level.width)
                 for y in range(dungeon_level.height)]
    random.shuffle(positions)
    for position in positions:
        x, y = position
        move_succeeded = piece.try_move((x, y), dungeon_level)
        if(move_succeeded):
            return True
    return False


def spawn_rat_man(dungeon_level):
    rat = monster.RatMan()
    spawn_succeded = place_piece_on_random_tile(rat, dungeon_level)
    if(not spawn_succeded):
        logging.info("could not spawn rat-man")
        return False
    return True
