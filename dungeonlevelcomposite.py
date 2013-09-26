from compositecore import Leaf, CompositeMessage


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
        if(not self.dungeon_level is value):
            self._dungeon_level = value
            if(not self.parent is None):
                self._dungeon_level.add_actor_if_not_present(self.parent)
                self.parent.message(CompositeMessage.DUNGEON_LEVEL_CHANGED)

    def on_parent_changed(self):
        """
        When the parent changes try to add it to the dungeon.
        """
        if(not self.dungeon_level is None):
            self.dungeon_level.add_actor_if_not_present(self.parent)
