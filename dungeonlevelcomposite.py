from compositecore import Leaf, CompositeMessage


class DungeonLevel(Leaf):
    """
    Composites holding this is in a DungeonLevel.
    """
    def __init__(self):
        super(DungeonLevel, self).__init__()
        self.component_type = "dungeon_level"
        self._value = None

    @property
    def value(self):
        """
        Gets the dungeon_level the entity is currently in.
        """
        return self._value

    @value.setter
    def value(self, new_dungeon_level):
        """
        Sets current dungeon_level of the entity.
        Also updates the visibility/solidity of the dungeon_level tiles.
        """
        if(not self._value is new_dungeon_level):
            old_dungeon_level = self._value
            self._value = new_dungeon_level
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
                self.value.add_actor_if_not_present(self.parent)

    def on_parent_changed(self):
        """
        When the parent changes try to add it to the dungeon.
        """
        if(not self.value is None and self.has_sibling("actor")):
            self.value.add_actor_if_not_present(self.parent)
