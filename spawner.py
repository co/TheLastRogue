import random
import dungeontrash
import monster
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


def spawn_rat_man(dungeon_level, game_state):
    rat = monster.RatMan(game_state)
    spawn_succeded = place_piece_on_random_tile(rat, dungeon_level)
    if(not spawn_succeded):
        logging.info("could not spawn rat-man")
        return False
    return True


def spawn_corpse_of_entity(entity_killed):
    return spawn_corpse_on_position(entity_killed.position,
                                    entity_killed.dungeon_level)


def spawn_corpse_on_position(position, dungeon_level):
    corpse = dungeontrash.Corpse()
    spawn_succeded = corpse.try_move(position, dungeon_level)
    if(not spawn_succeded):
        logging.info("could not spawn corpse.")
        return False
    return True
