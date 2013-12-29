import random
import logging
from stats import GamePieceType

import dungeontrash
import item
import monster
import rng


def place_piece_on_random_tile(piece, dungeon_level):
    positions = [(x, y) for x in range(dungeon_level.width)
                 for y in range(dungeon_level.height)]
    random.shuffle(positions)
    for position in positions:
        x, y = position
        move_succeeded = piece.mover.try_move((x, y), dungeon_level)
        if move_succeeded:
            return True
    return False


def spawn_rat_man(dungeon_level, game_state):
    rat = monster.Ratman(game_state)
    spawn_succeeded = place_piece_on_random_tile(rat, dungeon_level)
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


def place_health_potions(dungeon_level):
    health_potions_to_spawn = 0

    for _ in range(2):
        if rng.coin_flip():
            health_potions_to_spawn += 1
    if dungeon_level.depth == 0:
        health_potions_to_spawn += 2
    health_potions_to_spawn += 1
    for _ in range(health_potions_to_spawn):
        potion = item.HealthPotion()
        place_piece_on_random_tile_not_on_item_or_feature(potion, dungeon_level)
    #print "HP pots spawned: ", health_potions_to_spawn


def place_equipment(dungeon_level):
    depth = dungeon_level.depth

    if (depth == 0 or depth == 1) and rng.coin_flip():
        early_weapon = random.choice([item.Knife(), item.Sling()])
        place_piece_on_random_tile(early_weapon, dungeon_level)

    for _ in range(random.randrange(depth + 1)):
        if rng.coin_flip():
            if rng.coin_flip() and rng.coin_flip() and rng.coin_flip():  # Rare equipment.
                equipment = random.choice([item.Sword(), item.Gun()])
            else:  # Common equipment.
                equipment = random.choice([item.LeatherBoots(), item.LeatherCap(), item.LeatherArmor(),
                                           item.Knife(), item.Sling()])
            place_piece_on_random_tile(equipment, dungeon_level)


def place_ammo(dungeon_level):
    depth = dungeon_level.depth
    for _ in range(random.randrange(depth / 2 + 1)):
        if rng.coin_flip():
            ammo = item.Ammunition()
            place_piece_on_random_tile_not_on_item_or_feature(ammo, dungeon_level)


def place_jewellry(dungeon_level):
    depth = dungeon_level.depth
    for _ in range(random.randrange(depth + 1)):
        if rng.coin_flip() and rng.coin_flip() and rng.coin_flip():
            ring = random.choice([item.RingOfEvasion(), item.RingOfStealth(), item.RingOfEvasion()])
            place_piece_on_random_tile_not_on_item_or_feature(ring, dungeon_level)


def place_devices(dungeon_level):
    if rng.coin_flip() and rng.coin_flip():
        device = random.choice([item.DarknessDevice(), item.HeartStopDevice()])
        place_piece_on_random_tile(device, dungeon_level)


def place_items_in_dungeon(dungeon_level):
    place_health_potions(dungeon_level)
    place_ammo(dungeon_level)
    place_jewellry(dungeon_level)
    place_equipment(dungeon_level)
    place_devices(dungeon_level)


def place_piece_on_random_tile_not_on_item_or_feature(piece, dungeon_level):
    positions = [(x, y) for x in range(dungeon_level.width)
                 for y in range(dungeon_level.height)]
    random.shuffle(positions)
    for position in positions:
        x, y = position
        tile = dungeon_level.get_tile(position)
        if (tile.has_piece_of_type(GamePieceType.ITEM) or
                tile.has_piece_of_type(GamePieceType.DUNGEON_FEATURE)):
            continue
        move_succeeded = piece.mover.try_move((x, y), dungeon_level)
        if move_succeeded:
            return True
    return False
