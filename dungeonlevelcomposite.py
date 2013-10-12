from compositecore import Leaf, CompositeMessage


class DungeonLevel(Leaf):
    """
    Composites holding this has a position in the dungeon.
    """
    def __init__(self):
        super(DungeonLevel, self).__init__()
        self.component_type = "dungeon_level"
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
        print "moving to dungeon_level: ", value, " from: ", self._dungeon_level, self.parent
        if(not self._dungeon_level is value):
            print "it was new!"
            old_dungeon_level = self._dungeon_level
            print value
            self._dungeon_level = value
            print "n", self.dungeon_level, self._dungeon_level
            self._signal_dungeon_level_changed()
            if(not old_dungeon_level is None and
               self.has_sibling("actor")):
                old_dungeon_level.remove_actor_if_present(self.parent)

    def _signal_dungeon_level_changed(self):
        """
        Is called when dungeon level has changed.
        """
        if(not self.parent is None):
            self.parent.message(CompositeMessage.DUNGEON_LEVEL_CHANGED)
            if(self.has_sibling("actor")):
                self._dungeon_level.add_actor_if_not_present(self.parent)

    def on_parent_changed(self):
        """
        When the parent changes try to add it to the dungeon.
        """
        if(not self.dungeon_level is None and self.has_sibling("actor")):
            print "added as actor", self.parent
            self.dungeon_level.add_actor_if_not_present(self.parent)
