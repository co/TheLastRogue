import random
from monster import new_ratman, new_ghost, new_slime, new_dark_slime, new_dust_demon, new_spider, new_salamander, new_cyclops, AddGhostReviveToSeenEntities


class DungeonTableItem(object):
    def __init__(self, monster_factory_function):
        self.monster_function = monster_factory_function

        tmp_entity = self.monster_function(None)
        self.minimum_depth = tmp_entity.minimum_depth.value


# Weighted by the factor.
dungeon_table =\
    (
        [DungeonTableItem(new_ratman)] * 30 +
        [DungeonTableItem(new_ghost)] * 8 +
        [DungeonTableItem(new_slime)] * 3 +
        [DungeonTableItem(new_dark_slime)] * 2 +
        [DungeonTableItem(new_dust_demon)] * 5 +
        [DungeonTableItem(new_spider)] * 15 +
        [DungeonTableItem(new_salamander)] * 3 +
        [DungeonTableItem(new_cyclops)] * 3
    )


def filter_monster_table_by_depth(table, depth):
    return [table_item for table_item in table if table_item.minimum_depth <= depth]


def from_table_pick_n_monsters_for_depth(table, n, depth, game_state):
    filtered_table = filter_monster_table_by_depth(table, depth)
    return [random.choice(filtered_table).monster_function(game_state) for _ in range(n)]
