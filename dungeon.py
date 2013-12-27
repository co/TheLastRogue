import random
import dungeongenerator
from geometry import add_2d
import spawner
import monster
import rng
import item
from tools import time_it


class Dungeon(object):
    def __init__(self, game_state):
        self.level_count = 10
        self._dungeon_levels = []
        self.game_state = game_state

    def get_dungeon_level(self, depth):
        if depth >= self.level_count:
            self.game_state.has_won = True
            return None
        if len(self._dungeon_levels) <= depth:
            self._dungeon_levels.append(self._generate_dungeon_level(depth))
        return self._dungeon_levels[depth]

    def _generate_dungeon_level(self, depth):
        self.game_state.draw_loading_screen("Generating Dungeon...")
        size = 600 + depth * 20

        dungeon_level = time_it("dungeon_level_generation",
                                (lambda: dungeongenerator.generate_dungeon_exploded_rooms(size, depth)))
        for _ in range(int(depth * 1.5) + 4):
            if rng.coin_flip() and rng.coin_flip():
                ghost = monster.Ghost(self.game_state)
                spawner.place_piece_on_random_tile(ghost, dungeon_level)
            else:
                spawner.spawn_rat_man(dungeon_level, self.game_state)

        for _ in range(random.randrange(depth, depth + 2) - 1):
            if rng.coin_flip() and rng.coin_flip():
                cyclops = monster.Cyclops(self.game_state)
                spawner.place_piece_on_random_tile(cyclops, dungeon_level)

        for _ in range(random.randrange(int(depth / 2), int(depth / 2) + 3) - 1):
            if rng.coin_flip() or rng.coin_flip():
                slime = monster.Slime(self.game_state)
                spawner.place_piece_on_random_tile(slime, dungeon_level)

        if depth == (len(self._dungeon_levels) - 1):
            jericho = monster.Jericho(self.game_state)
            spawner.place_piece_on_random_tile(jericho, dungeon_level)

        spawner.place_items_in_dungeon(dungeon_level)

        dungeon_level.print_statistics()

        dungeon_level.dungeon = self
        return dungeon_level
