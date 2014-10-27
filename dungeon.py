import random

import dungeongenerator
from monsteractor import TryPutToSleep
from monstertables import from_table_pick_n_items_for_depth, dungeon_table, dungeon_equipment_table, dungeon_usable_item_table
import spawner
from tools import time_it


class Dungeon(object):
    def __init__(self, game_state):
        self.level_count = 10
        self._dungeon_levels = [None]
        self.game_state = game_state

    def get_dungeon_level(self, depth):
        if depth >= self.level_count:
            self.game_state.has_won = True
            return None
        while len(self._dungeon_levels) <= depth:
            self._dungeon_levels.append(self._generate_dungeon_level(len(self._dungeon_levels)))
        return self._dungeon_levels[depth]

    def __getstate__(self):
        return dict(self.__dict__)

    def __setstate__(self, state):
        self.__dict__.update(state)

    def _generate_dungeon_level(self, depth):
        self.game_state.draw_loading_screen("Generating Dungeon...")
        size = 600 + depth * 20

        dungeon_level = time_it("dungeon_level_generation",
                                (lambda: dungeongenerator.generate_dungeon_floor(size, depth)))
        minimum_monsters = int(4 + depth * 1.2)
        monsters_to_spawn = random.randrange(minimum_monsters, minimum_monsters + 3)
        monsters = from_table_pick_n_items_for_depth(dungeon_table, monsters_to_spawn,
                                                     depth, self.game_state)
        print monsters
        for monster in monsters:
            sleep_chance = 0.25
            if sleep_chance > random.random():
                monster.set_child(TryPutToSleep())
            spawner.place_piece_on_random_walkable_tile(monster, dungeon_level)

        if depth == (len(self._dungeon_levels) - 1):
            jericho = monster.new_jericho(self.game_state)
            spawner.place_piece_on_random_walkable_tile(jericho, dungeon_level)

        place_items_in_dungeon(dungeon_level, self.game_state)

        #dungeon_level.print_statistics()

        dungeon_level.dungeon = self
        return dungeon_level


def place_items_in_dungeon(dungeon_level, game_state):
    spawner.place_health_potions(dungeon_level, game_state)
    equipments = from_table_pick_n_items_for_depth(dungeon_equipment_table,
                                                   random.randrange(int(2 + dungeon_level.depth * 0.5)),
                                                   dungeon_level.depth, game_state)
    usable_items = from_table_pick_n_items_for_depth(dungeon_usable_item_table,
                                                     random.randrange(int(3 + dungeon_level.depth * 0.3)),
                                                     dungeon_level.depth, game_state)
    for loot_item in equipments + usable_items:
        print "item: ", loot_item.description.name
        spawner.place_piece_on_random_walkable_tile(loot_item, dungeon_level)


class ReflexiveDungeon(object):
    def __init__(self, dungeon_level):
        self.dungeon_level = dungeon_level
        self.dungeon_level.dungeon = self

    def get_dungeon_level(self, depth):
        return self.dungeon_level
