from compositecore import Leaf

ITEM_CAPACITY = 16


class Inventory(Leaf):
    """
    Holds the Items an entity is carrying.
    """
    def __init__(self):
        super(Inventory, self).__init__()
        self._items = []
        self._entity = self.parent
        self._item_capacity = ITEM_CAPACITY
        self.component_type = "inventory"

    @property
    def items(self):
        return self._items

    def try_add(self, item):
        """
        Tries to add an item to the inventory.

        Returns True on success otherwise False.
        """
        if(not self.has_room_for_item()):
            return False
        else:
            if not item.dungeon_level.value is None:
                success = item.mover.try_remove_from_dungeon()
                if not success:
                    raise Exception("ERROR: Tried to remove item: "
                                    + str(item) + "but could not.")
            self._items.append(item)
            return True

    def has_room_for_item(self):
        """
        Returns true if the inventory has room for another item.
        """
        return len(self._items) + 1 <= self._item_capacity

    def can_drop_item(self, item):
        """
        Returns true if it is a legal action to drop the item.
        """
        return item.mover.can_move(self._entity.position,
                                   self._entity.dungeon_level)

    def try_drop_item(self, item):
        """
        Tries to drop an item to the ground.

        Returns True on success otherwise False.
        """
        drop_successful = item.mover.try_move(self._entity.position,
                                              self._entity.dungeon_level)
        if drop_successful:
            self.remove_item(item)
        return drop_successful

    def remove_item(self, item):
        """
        Removes item from the inventory.
        """
        self._items.remove(item)

    def has_item(self, item):
        """
        Returns true if the item instance is in the inventory, false otherwise.
        """
        return item in self._items

    def is_empty(self):
        """
        Returns true the inventory is empty, false otherwise.
        """
        return len(self._items) <= 0

    def items_of_equipment_type(self, type_):
        """
        Returns a list of all items in the inventory of the given type.
        """
        return [item for item in self._items
                if item.has_child("equipment_type") and
                item.equipment_type.value == type_]
