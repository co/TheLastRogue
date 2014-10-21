import random
import item
import monster
from weapon import new_dagger, new_sword, new_gun, new_sling, new_kris, new_katar, new_cestus, new_iron_hand, new_spear, new_claw, new_morning_star, new_rapier, new_scimitar, new_club, new_flail, new_hammer, new_chain_and_ball, new_trident, new_whip, new_axe


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


dungeon_armor_table = \
    (
        [DungeonTableItem(item.new_leather_boots)] * 10 +
        [DungeonTableItem(item.new_boots_of_running)] * 4 +
        [DungeonTableItem(item.new_boots_of_sneaking)] * 4 +
        [DungeonTableItem(item.new_leather_cap)] * 10 +
        [DungeonTableItem(item.new_leather_armor)] * 10
    )

dungeon_jewellry_table = \
    (
        [DungeonTableItem(item.new_ring_of_evasion)] * 10 +
        [DungeonTableItem(item.new_ring_of_stealth)] * 10 +
        [DungeonTableItem(item.new_ring_of_strength)] * 10 +

        [DungeonTableItem(item.new_amulet_of_reflect_damage)] * 6 +
        [DungeonTableItem(item.new_amulet_of_life_steal)] * 6
    )

dungeon_weapon_table = \
    (
        # Common Weapons:
        [DungeonTableItem(new_dagger)] * 9 +
        [DungeonTableItem(new_sword)] * 7 +
        [DungeonTableItem(new_spear)] * 7 +
        [DungeonTableItem(new_sling)] * 7 +
        [DungeonTableItem(new_axe)] * 7 +
        [DungeonTableItem(new_club)] * 7 +

        [DungeonTableItem(new_whip)] * 5 +
        [DungeonTableItem(new_cestus)] * 5 +

        # Uncommon Weapons:
        [DungeonTableItem(new_kris)] * 3 +
        [DungeonTableItem(new_katar)] * 3 +
        [DungeonTableItem(new_morning_star)] * 3 +
        [DungeonTableItem(new_iron_hand)] * 3 +
        [DungeonTableItem(new_claw)] * 3 +
        [DungeonTableItem(new_rapier)] * 3 +
        [DungeonTableItem(new_scimitar)] * 3 +
        [DungeonTableItem(new_flail)] * 3 +
        [DungeonTableItem(new_hammer)] * 3 +
        [DungeonTableItem(new_chain_and_ball)] * 3 +
        [DungeonTableItem(new_trident)] * 3 +
        [DungeonTableItem(new_gun)] * 3
    )

dungeon_usable_item_table = \
    (
        [DungeonTableItem(item.new_ammunition)] * 10 +
        [DungeonTableItem(item.new_energy_sphere)] * 7 +

        [DungeonTableItem(item.new_darkness_device)] * 2 +
        [DungeonTableItem(item.new_heart_stop_device)] * 2 +
        [DungeonTableItem(item.new_glass_device)] * 2 +
        [DungeonTableItem(item.new_zap_device)] * 2 +
        [DungeonTableItem(item.new_healing_device)] * 2 +
        [DungeonTableItem(item.new_swap_device)] * 2 +
        [DungeonTableItem(item.new_blinks_device)] * 2 +

        [DungeonTableItem(item.new_bomb)] * 4 +
        [DungeonTableItem(item.new_poison_potion)] * 6 +
        [DungeonTableItem(item.new_flame_potion)] * 6 +

        [DungeonTableItem(item.new_teleport_scroll)] * 8 +
        [DungeonTableItem(item.new_map_scroll)] * 8 +
        [DungeonTableItem(item.new_swap_scroll)] * 8
    )

# Weighted by the factor.
dungeon_equipment_table = \
    (
        dungeon_armor_table * 8 +
        dungeon_jewellry_table * 4 +
        dungeon_weapon_table * 12
    )

