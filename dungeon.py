import random
import dungeongenerator
import spawner
import monster
import rng
import item
from tools import time_it


class Dungeon(object):
    def __init__(self, game_state):
        level_count = 5
        self._dungeon_levels = [None for _ in range(level_count)]
        self.game_state = game_state

    @property
    def level_count(self):
        return len(self._dungeon_levels)

    def get_dungeon_level(self, depth):
        if depth >= self.level_count:
            self.game_state.has_won = True
            return None
        if self._dungeon_levels[depth] is None:
            self._dungeon_levels[depth] = self._generate_dungeon_level(depth)
        return self._dungeon_levels[depth]

    def remove_dungeon_level(self, depth):
        """
        Hack to improve save speed, I don't think I need past levels anyway...
        """
        self._dungeon_levels[depth] = None

    def _generate_dungeon_level(self, depth):
        size = 700

        dungeon_level = time_it("dungeon_level_generation",
                                (lambda: dungeongenerator.generate_dungeon_exploded_rooms(size, depth)))
        for _ in range(depth + 4):
            if rng.coin_flip() and rng.coin_flip():
                ghost = monster.Ghost(self.game_state)
                spawner.place_piece_on_random_tile(ghost, dungeon_level)
            else:
                spawner.spawn_rat_man(dungeon_level, self.game_state)

        for _ in range(random.randrange(depth + 2)):
            if rng.coin_flip() and rng.coin_flip():
                cyclops = monster.Cyclops(self.game_state)
                spawner.place_piece_on_random_tile(cyclops, dungeon_level)

        for _ in range(random.randrange(depth + 2)):
            if rng.coin_flip():
                slime = monster.Slime(self.game_state)
                spawner.place_piece_on_random_tile(slime, dungeon_level)

        if depth == (len(self._dungeon_levels) - 1):
            jerico = monster.Jerico(self.game_state)
            spawner.place_piece_on_random_tile(jerico, dungeon_level)

        spawner.place_items_in_dungeon(dungeon_level)

        dungeon_level.dungeon = self
        return dungeon_level
