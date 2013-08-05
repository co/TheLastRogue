import dungeongenerator
import monster
import rng
import item
import spawner


class Dungeon(object):
    def __init__(self, game_state):
        level_count = 5
        self._dungeon_levels = [None for _ in range(level_count)]
        self.game_state = game_state

    @property
    def level_count(self):
        return len(self._dungeon_levels)

    def get_dungeon_level(self, depth):
        if(depth >= self.level_count):
            self.game_state.has_won = True
            return None
        if self._dungeon_levels[depth] is None:
            self._dungeon_levels[depth] = self._generate_dungeon_level(depth)
        return self._dungeon_levels[depth]

    def _generate_dungeon_level(self, depth):
        size = 700
        dungeon_level = dungeongenerator.generate_dungeon_exploded_rooms(size,
                                                                         depth)
        for _ in range(2 * (depth + 1) + 1):
            spawner.spawn_rat_man(dungeon_level, self.game_state)

        for _ in range(depth + 3):
            potion = item.HealthPotion()
            spawner.place_piece_on_random_tile(potion, dungeon_level)

        if rng.coin_flip():
            gun = item.Gun()
            spawner.place_piece_on_random_tile(gun, dungeon_level)

        if depth == (len(self._dungeon_levels) - 1):
            jerico = monster.Jerico(self.game_state)
            spawner.place_piece_on_random_tile(jerico, dungeon_level)

        statue = monster.StoneStatue(self.game_state)
        spawner.place_piece_on_random_tile(statue, dungeon_level)

        dungeon_level.dungeon = self
        return dungeon_level
