import random
import item
import monster


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
        [DungeonTableItem(monster.new_ratman)] * 30 +
        [DungeonTableItem(monster.new_ratman_mystic)] * 3 +
        [DungeonTableItem(monster.new_ghost)] * 8 +
        [DungeonTableItem(monster.new_slime)] * 3 +
        [DungeonTableItem(monster.new_dark_slime)] * 2 +
        [DungeonTableItem(monster.new_pixie)] * 2 +
        [DungeonTableItem(monster.new_armored_beetle)] * 3 +
        [DungeonTableItem(monster.new_dust_demon)] * 5 +
        [DungeonTableItem(monster.new_spider)] * 12 +
        [DungeonTableItem(monster.new_salamander)] * 3 +
        [DungeonTableItem(monster.new_cyclops)] * 3
    )


def filter_monster_table_by_depth(table, depth):
    return [table_item for table_item in table if table_item.minimum_depth <= depth]


def from_table_pick_n_items_for_depth(table, n, depth, game_state):
    filtered_table = filter_monster_table_by_depth(table, depth)
    return [random.choice(filtered_table).creator(game_state) for _ in range(n)]


# Weighted by the factor.
dungeon_equipment_table = \
    (
        [DungeonTableItem(item.new_leather_boots)] * 10 +
        [DungeonTableItem(item.new_boots_of_running)] * 2 +
        [DungeonTableItem(item.new_boots_of_sneaking)] * 2 +
        [DungeonTableItem(item.new_leather_cap)] * 10 +
        [DungeonTableItem(item.new_leather_armor)] * 10 +

        [DungeonTableItem(item.new_dagger)] * 8 +
        [DungeonTableItem(item.new_sling)] * 8 +

        [DungeonTableItem(item.new_ring_of_evasion)] * 3 +
        [DungeonTableItem(item.new_ring_of_stealth)] * 3 +
        [DungeonTableItem(item.new_ring_of_strength)] * 3 +

        [DungeonTableItem(item.new_amulet_of_reflect_damage)] * 2 +
        [DungeonTableItem(item.new_amulet_of_life_steal)] * 2 +

        [DungeonTableItem(item.new_sword)] * 2 +
        #[DungeonTableItem(new_mace)] * 1 +
        [DungeonTableItem(item.new_gun)] * 2
    )

dungeon_usable_item_table = \
    (
        [DungeonTableItem(item.new_ammunition)] * 10 +
        [DungeonTableItem(item.new_energy_sphere)] * 7 +

        [DungeonTableItem(item.new_darkness_device)] * 2 +
        [DungeonTableItem(item.new_heart_stop_device)] * 2 +
        [DungeonTableItem(item.new_glass_device)] * 2 +
        [DungeonTableItem(item.new_swap_device)] * 2 +

        [DungeonTableItem(item.new_bomb)] * 4 +
        [DungeonTableItem(item.new_poison_potion)] * 6 +
        [DungeonTableItem(item.new_flame_potion)] * 6 +

        [DungeonTableItem(item.new_teleport_scroll)] * 8 +
        [DungeonTableItem(item.new_map_scroll)] * 8
    )
