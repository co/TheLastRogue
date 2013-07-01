import messenger
import numpy


class EffectTypes(object):
    REMOVER = 0
    BLOCKER = 1
    STATUS_ADDER = 2
    DAMAGE = 3


class DamageTypes(object):
    PHYSICAL = 0
    MAGIC = 1


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
        if(self.time_to_live is numpy.inf):
            return
        self.time_to_live = self.time_to_live - 1
        if(self.time_to_live < 1):
            self.target_entity.effect_queue.remove(self)


class StatusFlagAdder(EntityEffect):
    def __init__(self, source_entity, target_entity,
                 status_flag, time_to_live=1):
        status_adder = [EffectTypes.STATUS_ADDER]
        super(StatusFlagAdder,
              self).__init__(source_entity,
                             target_entity,
                             time_to_live,
                             status_adder)
        self.status_flag = status_flag

    def update(self):
        self.target_entity.add_status(self.status_flag)
        self.tick()


class Damage(EntityEffect):
    def __init__(self, source_entity, target_entity, effect_types, damage,
                 damage_types=[DamageTypes.PHYSICAL], time_to_live=1):
        super(Damage, self).__init__(source_entity=source_entity,
                                     target_entity=target_entity,
                                     effect_types=[EffectTypes.DAMAGE],
                                     time_to_live=time_to_live)
        self.damage = damage
        self.damage_types = damage_types

    def message(self):
        message = "%s hits %s for %d damage." %\
            (self.source_entity.name, self.target_entity.name, self.damage)
        messenger.messenger.message(messenger.Message(message))

    def update(self):
        self.target_entity.hurt(self.damage)
        self.message()
        self.tick()
