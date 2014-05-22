from compositecore import Leaf, CompositeMessage
from dungeonlevelfactory import unknown_level_map
from stats import Flag
import terrain
from tile import Tile


class MemoryMap(Leaf):
    """
    A representation of the dungeon as seen by an entity.
    """
    def __init__(self):
        super(MemoryMap, self).__init__()
        self.component_type = "memory_map"
        self._memory_map = []

    def get_memory_of_map(self, dungeon_level):
        self._init_memory_map_if_not_set(dungeon_level)
        return self._memory_map[dungeon_level.depth]

    def has_seen_position(self, position):
        memory = self._memory_map[self.parent.dungeon_level.value.depth]
        tile = memory.get_tile_or_unknown(position)
        return tile.get_terrain() and tile.get_terrain().has("tile_seen")

    def tile_seen(self, position):
        memory = self._memory_map[self.parent.dungeon_level.value.depth]
        tile = memory.get_tile_or_unknown(position)
        if tile.get_terrain() and not tile.get_terrain().has("tile_seen"):
            tile.get_terrain().set_child(Flag("tile_seen"))

    def _init_memory_map_if_not_set(self, dungeon_level):
        """
        Lazily initiates unknown dungeon to the depth needed.
        """
        depth = dungeon_level.depth
        while len(self._memory_map) <= depth:
            self._memory_map.append(None)
        if self._memory_map[depth] is None:
            self._memory_map[depth] =\
                unknown_level_map(dungeon_level.width,
                                  dungeon_level.height,
                                  dungeon_level.depth)

    def update_memory_of_tile(self, tile, position, depth):
        """
        Writes the entity memory of a tile, to the memory map.
        """
        self._init_memory_map_if_not_set(self.parent.dungeon_level.value)
        x, y = position
        self._memory_map[depth].tile_matrix[y][x] = tile.copy()

    def gain_knowledge_of_terrain_of_tile(self, tile, position, depth):
        """
        Writes the entity memory of a tile, to the memory map.

        If position is out of range, do nothing
        """
        x, y = position
        self._init_memory_map_if_not_set(self.parent.dungeon_level.value)
        try:
            if (not self._memory_map[depth].tile_matrix[y][x].get_terrain() or
                    self._memory_map[depth].tile_matrix[y][x].get_terrain().has("is_unknown")):
                new_tile = Tile()
                new_tile.add(tile.get_terrain())
                self._memory_map[depth].tile_matrix[y][x] = new_tile
        except IndexError:
            pass

    def number_of_seen_tiles(self, depth):
        seen_tiles = []
        for row in self._memory_map[depth].tile_matrix:
            for t in row:
                if t and not t.get_terrain():
                    seen_tiles.append(t)
        return len(seen_tiles)

    def message(self, message):
        """
        Handles messages recieved.
        """
        if(message == CompositeMessage.DUNGEON_LEVEL_CHANGED):
            self._init_memory_map_if_not_set(self.parent. dungeon_level.value)
