ITEM_CAPACITY = 16


class Inventory(object):
    def __init__(self, entity):
        self._items = []
        self._entity = entity
        self._item_capacity = ITEM_CAPACITY

    @property
    def items(self):
        return self._items

    def try_add(self, item):
        if(self.has_room_for_item(item)):
            return False
        else:
            item.try_remove_from_dungeon()
            self._items.append(item)
            item.inventory = self
            return True

    def has_room_for_item(self, item):
        return len(self._items) + 1 > self._item_capacity

    def drop_item(self, item):
        item.try_move(self._entity.position, self._entity.dungeon_level)
        self.remove_item(item)

    def remove_item(self, item):
        self._items.remove(item)
        item.inventory = None

    def has_item(self, item):
        return item in self._items

    def is_empty(self):
        return len(self._items) <= 0
