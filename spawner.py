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


def place_equipment(dungeon_level, game_state):
    depth = dungeon_level.depth

    if (depth == 0 or depth == 1) and rng.coin_flip():
        early_weapon = random.choice([item.new_knife(game_state), item.new_sling(game_state)])
        place_piece_on_random_walkable_tile_not_on_item_or_feature(early_weapon, dungeon_level)

    for _ in range(random.randrange(depth + 1)):
        if rng.coin_flip():
            if rng.coin_flip() and rng.coin_flip() and rng.coin_flip():  # Rare equipment.
                equipment = random.choice([item.new_sword(game_state), item.new_gun(game_state)])
            else:  # Common equipment.
                equipment = random.choice([item.new_leather_boots(game_state), item.new_leather_cap(game_state),
                                           item.new_leather_armor(game_state), item.new_knife(game_state),
                                           item.new_sling(game_state)])
            place_piece_on_random_walkable_tile_not_on_item_or_feature(equipment, dungeon_level)


def place_ammo(dungeon_level, game_state):
    depth = dungeon_level.depth
    for _ in range(random.randrange(depth / 2 + 1)):
        if rng.coin_flip():
            ammo = item.new_ammunition(game_state)
            place_piece_on_random_walkable_tile_not_on_item_or_feature(ammo, dungeon_level)


def place_bomb(dungeon_level, game_state):
    depth = dungeon_level.depth
    for _ in range(random.randrange(depth / 2 + 2)):
        if rng.coin_flip():
            bomb = item.new_bomb(game_state)
            place_piece_on_random_walkable_tile_not_on_item_or_feature(bomb, dungeon_level)


def place_jewellry(dungeon_level, game_state):
    depth = dungeon_level.depth
    for _ in range(random.randrange(depth + 1)):
        if rng.coin_flip() and rng.coin_flip() and rng.coin_flip():
            ring = random.choice([item.new_ring_of_evasion(game_state), item.new_ring_of_stealth(game_state),
                                  item.new_ring_of_strength(game_state)])
            place_piece_on_random_walkable_tile_not_on_item_or_feature(ring, dungeon_level)


def place_devices(dungeon_level, game_state):
    if rng.coin_flip() and rng.coin_flip():
        device = random.choice([item.new_darkness_device(game_state), item.new_heart_stop_device(game_state)])
        place_piece_on_random_walkable_tile_not_on_item_or_feature(device, dungeon_level)


def place_items_in_dungeon(dungeon_level, game_state):
    place_health_potions(dungeon_level, game_state)
    place_ammo(dungeon_level, game_state)
    place_jewellry(dungeon_level, game_state)
    place_equipment(dungeon_level, game_state)
    place_devices(dungeon_level, game_state)


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
