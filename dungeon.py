import dungeongenerator


class Dungeon(object):
    def __init__(self, game_state):
        level_count = 3
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
        dungeon_level = dungeongenerator.generate_dungeon_level(depth)
        dungeon_level.dungeon = self
        return dungeon_level
