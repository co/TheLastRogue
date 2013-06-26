import messenger

PHYSICAL = 0
MAGIC = 0


class EffectQueue(object):
    def __init__(self):
        self._effect_queue = []

    def add(self, entity_effect):
        self._effect_queue.append(entity_effect)

    def remove(self, effect):
        self._effect_queue.remove(effect)

    def update(self):
        for effect in self._effect_queue:
            effect.update()


class EntityEffect(object):
    def __init__(self, source_entity=None, target_entity=None,
                 time_to_live=1, effect_types=[]):
        self.source_entity = source_entity
        self.target_entity = target_entity
        self.time_to_live = time_to_live
        self.effect_types = effect_types
        self.is_blocked = False

    def message(self):
        pass

    def update(self):
        pass

    def tick(self):
        self.time_to_live = self.time_to_live - 1
        if(self.time_to_live < 1):
            self.target_entity.effect_queue.remove(self)


class Damage(EntityEffect):
    def __init__(self, source_entity, target_entity, effect_types, damage):
        super(Damage, self).__init__(source_entity=source_entity,
                                     target_entity=target_entity,
                                     effect_types=[PHYSICAL],
                                     time_to_live=1)
        self.damage = damage

    def message(self):
        message = "%s hits %s for %d damage." %\
            (self.source_entity.name, self.target_entity.name, self.damage)
        messenger.messenger.message(messenger.Message(message))

    def update(self):
        self.target_entity.hurt(self.damage)
        self.message()
        self.tick()
