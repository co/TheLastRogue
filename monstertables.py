import random
from item import new_leather_boots, new_leather_cap, new_leather_armor, new_knife, new_sling, new_sword, new_gun, new_ring_of_evasion, new_ring_of_strength, new_ring_of_stealth, new_ammunition, new_darkness_device, new_heart_stop_device, new_bomb, new_teleport_scroll, new_poison_potion, new_flame_potion, new_map_scroll, new_amulet_of_reflect_damage
from monster import new_ratman, new_ghost, new_slime, new_dark_slime, new_dust_demon, new_spider, new_salamander, new_cyclops, AddGhostReviveToSeenEntities, new_pixie, new_armored_beetle


class DungeonTableItem(object):
    def __init__(self, creator):
        self.creator = creator

        tmp_entity = self.creator(None)
        if tmp_entity.has("minimum_depth"):
            self.minimum_depth = tmp_entity.minimum_depth.value
        else:
            self.minimum_depth = -1


# Weighted by the factor.
dungeon_table = \
    (
        [DungeonTableItem(new_ratman)] * 30 +
        [DungeonTableItem(new_ghost)] * 8 +
        [DungeonTableItem(new_slime)] * 3 +
        [DungeonTableItem(new_dark_slime)] * 2 +
        [DungeonTableItem(new_pixie)] * 2 +
        [DungeonTableItem(new_armored_beetle)] * 3 +
        [DungeonTableItem(new_dust_demon)] * 5 +
        [DungeonTableItem(new_spider)] * 12 +
        [DungeonTableItem(new_salamander)] * 3 +
        [DungeonTableItem(new_cyclops)] * 3
    )


def filter_monster_table_by_depth(table, depth):
    return [table_item for table_item in table if table_item.minimum_depth <= depth]


def from_table_pick_n_items_for_depth(table, n, depth, game_state):
    filtered_table = filter_monster_table_by_depth(table, depth)
    return [random.choice(filtered_table).creator(game_state) for _ in range(n)]


# Weighted by the factor.
dungeon_equipment_table = \
    (
        [DungeonTableItem(new_leather_boots)] * 10 +
        [DungeonTableItem(new_leather_cap)] * 10 +
        [DungeonTableItem(new_leather_armor)] * 10 +

        [DungeonTableItem(new_knife)] * 8 +
        [DungeonTableItem(new_sling)] * 8 +

        [DungeonTableItem(new_ring_of_evasion)] * 3 +
        [DungeonTableItem(new_ring_of_stealth)] * 3 +
        [DungeonTableItem(new_ring_of_strength)] * 3 +

        [DungeonTableItem(new_amulet_of_reflect_damage)] * 2 +

        [DungeonTableItem(new_sword)] * 2 +
        [DungeonTableItem(new_gun)] * 2
    )

dungeon_usable_item_table = \
    (
        [DungeonTableItem(new_ammunition)] * 10 +

        [DungeonTableItem(new_darkness_device)] * 3 +
        [DungeonTableItem(new_heart_stop_device)] * 3 +

        [DungeonTableItem(new_bomb)] * 4 +
        [DungeonTableItem(new_poison_potion)] * 6 +
        [DungeonTableItem(new_flame_potion)] * 6 +

        [DungeonTableItem(new_teleport_scroll)] * 8 +
        [DungeonTableItem(new_map_scroll)] * 8
    )
