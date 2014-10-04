EQUIP_MESSAGE = "%(source_entity)s equips %(item)s."
UNEQUIP_MESSAGE = "%(source_entity)s puts away %(item)s."
HEAL_MESSAGE = "%(source_entity)s heals %(target_entity)s for %(health)s health."
HEALTH_POTION_MESSAGE = "The health potion heals %(target_entity)s for %(health)s health."
DISSOLVE_MESSAGE = "%(source_entity)s dissolves %(target_entity)s for %(damage)s damage."
HIT_MESSAGE = "%(source_entity)s hits %(target_entity)s for %(damage)s damage."
MISS_MESSAGE = "%(source_entity)s misses %(target_entity)s."
CRIT_MESSAGE = "%(source_entity)s critically hits %(target_entity)s for %(damage)s damage."

HAUNT_MESSAGE = "%(source_entity)s haunts the %(target_entity)s!"

HEART_STOP_MESSAGE = "%(target_entity)s, clutches its heart."
DARKNESS_MESSAGE = "An unnatural darkness fills the dungeon."
PICK_UP_MESSAGE = "You pick up %(item)s."
POISON_MESSAGE = "%(target_entity)s takes %(damage)s in poison damage."
BLEED_MESSAGE = "%(target_entity)s is bleeding out %(damage)s damage."

DOWN_STAIRS_HEAL_MESSAGE = "Your feel vitalized by your progress, you regain %(health)s health."
FALL_DOWN_MESSAGE = "You take a damage of %(damage)s from the fall."
DRINK_FOUNTAIN_MESSAGE = "You drink from the fountain, your max health increases by %(health)s."

HURT_BY_EXPLOSION = "The explosion blasts %(target_entity)s for %(damage)s damage."
HURT_BY_FIRE = "The fire burns %(target_entity)s for %(damage)s damage."

WONT_BREAK_OUT_OF_WEB_MESSAGE = "%(target_entity)s is stuck in the spider web."
BREAKS_OUT_OF_WEB_MESSAGE = "%(target_entity)s breaks free."

WANT_TO_JUMP_DOWN_CHASM = "Are you sure you want to drop down the chasm?"
PRESS_ENTER_TO_ACCEPT = "Press ENTER to accept, another key to reject."

PLAYER_TELEPORT_MESSAGE = "Your surroundings seem different."

POTION_SMASH_TO_GROUND = "The %(target_entity)s smashes to the ground and breaks into pieces."
ITEM_HITS_THE_GROUND = "The %(target_entity)s hits the ground with a thud."
ENTITY_EXPLODES = "The %(target_entity)s explodes!"

PLAYER_MAP_MESSAGE = "You surroundings suddenly seem familiar."
GLASS_TURNING_MESSAGE = "You surroundings suddenly seem more transparent."


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
        new_message = Message(new_message.capitalize())
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
