import messenger
from statusflags import StatusFlags
from compositecore import Leaf
import random


# Effect types in execution order
class EffectTypes(object):
    STATUS_REMOVER = 0
    BLOCKER = 1
    STATUS_ADDER = 2
    TELEPORT = 3
    HEAL = 4
    DAMAGE = 5
    EQUIPMENT = 6

    ALLTYPES = [STATUS_REMOVER, BLOCKER, STATUS_ADDER,
                TELEPORT, HEAL, DAMAGE, EQUIPMENT]


class EffectQueue(Leaf):
    def __init__(self):
        super(EffectQueue, self).__init__()
        self.component_type = "effect_queue"
        self._effect_queue = [None for x in range(len(EffectTypes.ALLTYPES))]
        for effect_type in EffectTypes.ALLTYPES:
            self._effect_queue[effect_type] = []

    def add(self, effect):
        self._effect_queue[effect.effect_type].append(effect)
        effect.queue = self

    def remove(self, effect):
        self._effect_queue[effect.effect_type].remove(effect)
        effect.queue = None

    def remove_status_adder_of_status(self, status_to_remove):
        for effect in self._effect_queue[EffectTypes.STATUS_ADDER]:
            if(effect.status_flag == status_to_remove):
                self._effect_queue[EffectTypes.STATUS_ADDER].remove(effect)

    def update(self, time_spent):
        for effect_type_queue in EffectTypes.ALLTYPES:
            for effect in self._effect_queue[effect_type_queue]:
                effect.update(time_spent)


class EntityEffect(object):
    def __init__(self, source_entity, time_to_live, effect_type):
        self.source_entity = source_entity
        self.time_to_live = time_to_live
        self.effect_type = effect_type
        self.is_blocked = False
        self.queue = None

    def update(self, time_spent):
        pass

    def tick(self, time_spent):
        self.time_to_live = self.time_to_live - time_spent
        if(self.time_to_live < 1):
            self.queue.remove_entity_effect(self)


class StatusRemover(EntityEffect):
    def __init__(self, source_entity,
                 status_type_to_remove, time_to_live=1):
        super(StatusRemover,
              self).__init__(source_entity,
                             time_to_live,
                             EffectTypes.STATUS_REMOVER)
        self.status_type_to_remove = status_type_to_remove

    def update(self, time_spent):
        self.queue.remove_status_adder_of_status(self.status_type_to_remove)
        self.tick(time_spent)


class StatusAdder(EntityEffect):
    def __init__(self, source_entity, status_flag, time_to_live=1):
        super(StatusAdder, self).__init__(source_entity, time_to_live,
                                          EffectTypes.STATUS_ADDER)
        self.status_flag = status_flag

    def update(self, time_spent):
        status_flags = StatusFlags(self.status_flag)
        status_flags.to_be_removed = True
        self.parent.add_child(status_flags)
        self.tick(time_spent)


class Teleport(EntityEffect):
    def __init__(self, source_entity,
                 time_to_live=1):
        super(Teleport,
              self).__init__(source_entity,
                             time_to_live,
                             EffectTypes.TELEPORT)

    def update(self, time_spent):
        positions = self.parent.dungeon_level.get_walkable_positions()
        random_positions = random.sample(positions, len(positions))
        for position in random_positions:
            teleport_successful = self.parent.mover.try_move(position)
            if teleport_successful:
                break
        self.tick(time_spent)


class DamageEntityEffect(EntityEffect):
    def __init__(self, source_entity, damage,
                 damage_types, time_to_live=1):
        super(DamageEntityEffect,
              self).__init__(source_entity=source_entity,
                             effect_type=EffectTypes.DAMAGE,
                             time_to_live=time_to_live)
        self.damage = damage
        self.damage_types = damage_types

    def message(self):
        message = "%s hits %s for %d damage." %\
            (self.source_entity.description.name,
             self.parent.description.name, self.damage)
        messenger.messenger.message(message)

    def update(self, time_spent):
        self.parent.health.hurt(self.damage)
        self.message()
        self.tick(time_spent)


class Heal(EntityEffect):
    def __init__(self, source_entity, health,
                 time_to_live=1):
        super(Heal, self).__init__(source_entity=source_entity,
                                   effect_type=EffectTypes.HEAL,
                                   time_to_live=time_to_live)
        self.health = health

    def message(self):
        message = "%s heals %s for %d health." %\
            (self.source_entity.description.name, self.parent.description.name,
             self.health)
        messenger.messenger.message(message)

    def update(self, time_spent):
        self.parent.health.heal(self.health)
        self.message()
        self.tick(time_spent)


class Equip(EntityEffect):
    def __init__(self, source_entity, item):
        super(Equip, self).__init__(source_entity=source_entity,
                                    effect_type=EffectTypes.EQUIPMENT,
                                    time_to_live=1)
        self.item = item

    def message(self):
        message = "%s equips %s." % (self.source_entity.description.name,
                                     self.item.name)
        messenger.messenger.message(message)

    def update(self, time_spent):
        equipment = self.parent.equipment
        equip_succeded = equipment.try_equip(self.item)
        if(equip_succeded):
            self.message()
            if(self.parent.inventory.has_item(self.item)):
                self.parent.inventory.remove_item(self.item)
        self.tick(time_spent)


class UnEquip(EntityEffect):
    def __init__(self, source_entity, equipment_slot):
        super(UnEquip, self).__init__(source_entity=source_entity,
                                      effect_type=EffectTypes.EQUIPMENT,
                                      time_to_live=1)
        self.item = source_entity.equipment.get(equipment_slot)
        self.equipment_slot = equipment_slot

    def message(self):
        message = "%s unequips %s." % (self.source_entity.name, self.item.name)
        messenger.messenger.message(message)

    def update(self, time_spent):
        equipment = self.parent.equipment
        if(equipment.can_unequip_to_inventory(self.equipment_slot)):
            unequip_succeded =\
                equipment.unequip_to_inventory(self.equipment_slot)
            if(unequip_succeded):
                self.message()
        self.tick(time_spent)


class ReEquip(EntityEffect):
    def __init__(self, source_entity, equipment_slot, item):
        super(ReEquip, self).__init__(source_entity=source_entity,
                                      effect_type=EffectTypes.EQUIPMENT,
                                      time_to_live=1)
        self.equipment_slot = equipment_slot
        self.item = item

    def message(self):
        message = "%s equips %s." % (self.source_entity.name, self.item.name)
        messenger.messenger.message(message)

    def update(self, time_spent):
        old_item = None
        if(self.source_entity.equipment.slot_is_equiped(self.equipment_slot)):
            old_item =\
                self.source_entity.equipment.unequip(self.equipment_slot)

        equipment = self.parent.equipment
        equip_succeded = equipment.try_equip(self.item)
        if(equip_succeded):
            self.message()
            if(self.source_entity.inventory.has_item(self.item)):
                self.source_entity.inventory.remove_item(self.item)

        if(not old_item is None):
            self.source_entity.inventory.try_add(old_item)
        self.tick(time_spent)
