import random
import logging
from compositecore import Composite
from mover import Mover
from stats import GamePieceTypes

import dungeontrash
import item
import monster
import rng
from statusflags import StatusFlags
from text import Description


def place_piece_on_random_walkable_tile(piece, dungeon_level):
    walker = piece
    if not piece.has("status_flags"):
        walker = dummy_player
    for position in dungeon_level.get_random_walkable_positions_in_dungeon(walker):
        move_succeeded = piece.mover.try_move(position, dungeon_level)
        if move_succeeded:
            return True
    return False


def spawn_rat_man(dungeon_level, game_state):
    rat = monster.new_ratman(game_state)
    spawn_succeeded = place_piece_on_random_walkable_tile(rat, dungeon_level)
    if not spawn_succeeded:
        logging.info("could not spawn rat-man")
        return False
    return True

def spawn_corpse_of_entity(entity_killed):
    return spawn_corpse_on_position(entity_killed.position.value,
                                    entity_killed.dungeon_level.last_dungeon_level)


def spawn_corpse_on_position(position, dungeon_level):
    corpse = dungeontrash.Corpse()
    spawn_succeeded = corpse.mover.replace_move(position, dungeon_level)
    if not spawn_succeeded:
        logging.info("could not spawn corpse.")
        return False
    return True


def place_health_potions(dungeon_level, game_state):
    health_potions_to_spawn = 0

    for _ in range(2):
        if rng.coin_flip():
            health_potions_to_spawn += 1
    if dungeon_level.depth == 0:
        health_potions_to_spawn += 2
    health_potions_to_spawn += 1
    for _ in range(health_potions_to_spawn):
        potion = item.new_health_potion(game_state)
        place_piece_on_random_walkable_tile_not_on_item_or_feature(potion, dungeon_level)
    #print "HP pots spawned: ", health_potions_to_spawn


def place_piece_on_random_walkable_tile_not_on_item_or_feature(piece, dungeon_level):
    walker = piece
    if not piece.has("status_flags"):
        walker = dummy_player
    for position in dungeon_level.get_random_walkable_positions_in_dungeon(walker):
        tile = dungeon_level.get_tile(position)
        if (tile.has_piece_of_type(GamePieceTypes.ITEM) or
                tile.has_piece_of_type(GamePieceTypes.DUNGEON_FEATURE)):
            continue
        move_succeeded = piece.mover.try_move(position, dungeon_level)
        if move_succeeded:
            return True
    return False

dummy_player = Composite()
dummy_player.set_child(StatusFlags([StatusFlags.CAN_OPEN_DOORS]))
dummy_player.set_child(Mover())
dummy_player.set_child(Description("player_dummy", "Just a dummy used for instead of player for calculations."))
