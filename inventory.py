ITEM_CAPACITY = 16


class Inventory(object):
    """
    Holds the Items an entity is carrying.
    """
    def __init__(self, entity):
        super(Inventory, self).__init__()
        self._items = []
        self._entity = entity
        self._item_capacity = ITEM_CAPACITY

    @property
    def items(self):
        return self._items

    def try_add(self, item):
        if(not self.has_room_for_item()):
            return False
        else:
            item.try_remove_from_dungeon()
            self._items.append(item)
            item.inventory = self
            return True

    def has_room_for_item(self):
        return len(self._items) + 1 <= self._item_capacity

    def can_drop_item(self, item):
        return item.can_move(self._entity.position,
                             self._entity.dungeon_level)

    def try_drop_item(self, item):
        drop_successful = item.try_move(self._entity.position,
                                        self._entity.dungeon_level)
        if drop_successful:
            self.remove_item(item)
        return drop_successful

    def remove_item(self, item):
        self._items.remove(item)
        item.inventory = None

    def has_item(self, item):
        return item in self._items

    def is_empty(self):
        return len(self._items) <= 0

    def items_of_equipment_type(self, type_):
        return [item for item in self._items if item.equipment_type == type_]
