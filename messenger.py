EQUIP_MESSAGE = "%(source_entity)s equips %(item)s."
UNEQUIP_MESSAGE = "%(source_entity)s puts away %(item)s."
HEAL_MESSAGE = "%(source_entity)s heals %(target_entity)s for %(health)s health."
HEALTH_POTION_MESSAGE = "The health potion heals %(target_entity)s for %(health)s health."
DISSOLVE_MESSAGE = "%(source_entity)s dissolves %(target_entity)s for %(damage)s damage."
HIT_MESSAGE = "%(source_entity)s hits %(target_entity)s for %(damage)s damage."
MISS_MESSAGE = "%(source_entity)s misses %(target_entity)s."

PICK_UP_MESSAGE = "You pick up %(item)s"

DOWN_STAIRS_HEAL_MESSAGE = "Your feel vitalized by your progress, you regain %(health)s health."
DRINK_FOUNTAIN_MESSAGE = "You drink from the fountain, your max health increases by %(health)s."


class Messenger(object):
    def __init__(self):
        self._messages = []
        self._has_new_message = False
        self.player = None

    @property
    def has_new_message(self):
        return self._has_new_message

    @has_new_message.setter
    def has_new_message(self, value):
        self._has_new_message = value

    def send_visual_message(self, new_message, position):
        if self.player.dungeon_mask.can_see_point(position):
            self._message(new_message)

    def send_global_message(self, new_message):
        self._message(new_message)

    def _message(self, new_message):
        new_message = Message(new_message)
        old_message = next((message for message in self._messages
                           if message.message == new_message.message and
                              message.ttl == new_message.ttl), None)
        if old_message:
            old_message.increase()
        else:
            self._messages.append(new_message)
        self.has_new_message = True

    def tail(self, length):
        self.has_new_message = False
        self._messages = [message for message in self._messages if message.ttl > 0]
        map(lambda m: m.tick(), self._messages)
        return self._messages[-length:]

    def clear(self):
        self._messages = []


class Message(object):
    def __init__(self, message):
        self.message = message
        self.count = 1
        self.ttl = 5

    def increase(self):
        self.count += 1

    def tick(self):
        self.ttl -= 1

    def __str__(self):
        if self.count > 1:
            return str(self.message) + " x" + str(self.count)
        return str(self.message)


msg = Messenger()
