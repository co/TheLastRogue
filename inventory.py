from compositecore import Leaf

ITEM_CAPACITY = 24


class Inventory(Leaf):
    """
    Holds the Items an entity is carrying.
    """

    def __init__(self):
        super(Inventory, self).__init__()
        self._items = []
        self._item_capacity = ITEM_CAPACITY
        self.component_type = "inventory"

    @property
    def items(self):
        return self._items

    def get_items_sorted(self):
        return sorted(self.items, key=lambda e: e.item_type.value)

    def add_item_no_stack(self, item):
        if not item.dungeon_level.value is None:
            success = item.mover.try_remove_from_dungeon()
            if not success:
                raise Exception("ERROR: Tried to remove item: " + str(item) + "but could not.")
        self._items.append(item)

    def try_stack_item(self, stackable_item):
        stackable_items = self.get_stackable_items_of_type(stackable_item.stacker.stack_type)
        for item in stackable_items:
            items_to_move = min(item.stacker.max_size - item.stacker.size, stackable_item.stacker.size)
            item.stacker.size += items_to_move
            stackable_item.stacker.size -= items_to_move
            if stackable_item.stacker.size == 0:
                break

    def try_add(self, item):
        """
        Tries to add an item to the inventory.

        Returns True on success otherwise False.
        """
        if not self.has_room_for_item(item):
            return False
        else:
            if item.has_child("stacker"):
                self.try_stack_item(item)
                if item.stacker.size == 0:
                    item.mover.try_remove_from_dungeon()
                    return True
            self.add_item_no_stack(item)
            return True

    def has_room_for_item(self, other_item):
        """
        Returns true if the inventory has room for another item.
        """
        stack_successful = False
        if other_item.has_child("stacker"):
            stack_successful = self.can_stack_new_item(other_item)
        return stack_successful or len(self._items) + 1 <= self._item_capacity

    def can_stack_new_item(self, stackable_item):
        stackable_items = self.get_stackable_items_of_type(stackable_item.stacker.stack_type)
        for item in stackable_items:
            if not item.stacker.is_full():
                return True
        return False

    def get_stackable_items_of_type(self, stack_type):
        return [item for item in self._items
                if item.has_child("stacker") and
                   item.stacker.stack_type == stack_type]

    def can_drop_item(self, item):
        """
        Returns true if it is a legal action to drop the item.
        """
        return item.mover.can_move(self.parent.position,
                                   self.parent.dungeon_level)

    def try_drop_item(self, item):
        """
        Tries to drop an item to the ground.

        Returns True on success otherwise False.
        """
        drop_successful = item.mover.try_move(self.parent.position.value,
                                              self.parent.dungeon_level.value)
        if drop_successful:
            self.remove_item(item)
        return drop_successful

    def remove_item(self, item):
        """
        Removes item from the inventory.
        """
        self._items.remove(item)

    def remove_one_item_from_stack(self, item):
        """
        Removes one instance of an item from the inventory.

        Works like remove_item but does not remove an entire stack of items.
        """
        if item.has_child("stacker"):
            item.stacker.size -= 1
            if item.stacker.size <= 0:
                self._items.remove(item)
        else:
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
