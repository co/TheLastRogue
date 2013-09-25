from compositecore import Leaf
from memorymap import MemoryMap
from dungeonmask import DungeonMask
import libtcodpy as libtcod


class DungeonLevel(Leaf):
    """
    Composites holding this has a position in the dungeon.
    """
    def __init__(self):
        super(DungeonLevel, self).__init__()
        self._dungeon_level = None

    @property
    def dungeon_level(self):
        """
        Gets the dungeon_level the entity is currently in.
        """
        return self._dungeon_level

    @dungeon_level.setter
    def dungeon_level(self, value):
        """
        Sets current dungeon_level of the entity.
        Also updates the visibility/solidity of the dungeon_level tiles.
        """
        if((not self.dungeon_level is value) and (not value is None)):
            self._dungeon_level = value
            dungeon_mask_module = self.get_sibling_of_type(DungeonMask)
            dungeon_mask_module.dungeon_map = libtcod.map_new(value.width,
                                                              value.height)
            dungeon_mask_module.update_dungeon_map()
            self.path = libtcod.path_new_using_map(self.dungeon_map, 1.0)
            if(self.has_sibling(MemoryMap)):
                self.get_sibling_of_type(MemoryMap).\
                    set_memory_map_if_not_set(self.dungeon_level)
