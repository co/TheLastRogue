import dungeongenerator


class Dungeon(object):
    def __init__(self):
        levels = 3
        self._dungeon_levels = [None for _ in range(levels)]

    def get_dungeon_level(self, depth):
        if self._dungeon_levels[depth] is None:
            self._dungeon_levels[depth] = self._generate_dungeon_level(depth)
        return self._dungeon_levels[depth]

    def _generate_dungeon_level(self, depth):
        return dungeongenerator.generate_dungeon_level(depth)
