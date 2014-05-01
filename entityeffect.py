from audioop import add
import random
import colors

from compositecore import Leaf
import gametime
from graphic import GraphicChar
import icon
import messenger
from statusflags import StatusFlags


# Effect types in execution order
class EffectTypes(object):
    STATUS_REMOVER = 0
    ADD_SPOOF_CHILD = 1
    BLOCKER = 2
    STATUS_ADDER = 3
    TELEPORT = 4
    HEAL = 5
    DAMAGE = 6
    EQUIPMENT = 7

    ALLTYPES = [STATUS_REMOVER, ADD_SPOOF_CHILD, BLOCKER, STATUS_ADDER,
                TELEPORT, HEAL, DAMAGE, EQUIPMENT]


class EffectStackID(object):
    SLIME_DISSOLVE = "slime_dissolve"


class EffectQueue(Leaf):
    def __init__(self):
        super(EffectQueue, self).__init__()
        self.component_type = "effect_queue"
        self._effect_queue = [None for _ in range(len(EffectTypes.ALLTYPES))]
        for effect_type in EffectTypes.ALLTYPES:
            self._effect_queue[effect_type] = []

    @property
    def effects(self):
        return [effect for effect_group in self._effect_queue for effect in effect_group]

    def add(self, effect):
        if effect.no_stack_id:
            if not any(effect.no_stack_id == e.no_stack_id for e in self.effects):
                self._add(effect)
        else:
            self._add(effect)

    def _add(self, effect):
        self._effect_queue[effect.effect_type].append(effect)
        effect.queue = self

    def remove(self, effect):
        self._effect_queue[effect.effect_type].remove(effect)
        effect.queue = None

    def remove_status_adder_of_status(self, status_to_remove):
        for effect in self._effect_queue[EffectTypes.STATUS_ADDER]:
            if effect.status_flag == status_to_remove:
                self._effect_queue[EffectTypes.STATUS_ADDER].remove(effect)

    def update(self, time):
        for effect_type_queue in EffectTypes.ALLTYPES:
            for effect in self._effect_queue[effect_type_queue]:
                effect.update(time)


class EntityEffect(object):
    def __init__(self, source_entity, time_to_live, effect_type, no_stack_id=None):
        self.source_entity = source_entity
        self.time_to_live = time_to_live
        self.effect_type = effect_type
        self.is_blocked = False
        self.no_stack_id = no_stack_id
        self.queue = None
        self.time_alive = 0

    def update(self, time_spent):
        pass

    @property
    def target_entity(self):
        return self.queue.parent

    def is_new_round(self, time_spent):
        turns_alive = int(self.time_alive / gametime.single_turn)
        new_turns_alive = int((self.time_alive + time_spent) / gametime.single_turn)
        return new_turns_alive > turns_alive

    def tick(self, time_spent):
        self.time_alive += time_spent
        self.time_to_live = self.time_to_live - time_spent
        if self.time_to_live < 1:
            self._on_remove_effect()
            self.queue.remove(self)

    def _on_remove_effect(self):
        pass


class StatusRemover(EntityEffect):
    def __init__(self, source_entity, status_type_to_remove, time_to_live=1):
        super(StatusRemover, self).__init__(source_entity,
                                            time_to_live,
                                            EffectTypes.STATUS_REMOVER)
        self.status_type_to_remove = status_type_to_remove

    def update(self, time_spent):
        self.queue.remove_status_adder_of_status(self.status_type_to_remove)
        self.tick(time_spent)


class HeartStop(EntityEffect):
    def __init__(self, source_entity, time_to_live=1, message=messenger.HEART_STOP_MESSAGE):
        super(HeartStop, self).__init__(source_entity, time_to_live, EffectTypes.STATUS_REMOVER)
        self.message = message

    def send_message(self):
        messenger.msg.send_visual_message(self.message % {"source_entity": self.source_entity.description.long_name,
                                                          "target_entity": self.target_entity.description.long_name},
                                          self.target_entity.position.value)

    def update(self, time_spent):
        if self.is_new_round(time_spent):
            gray_heart = GraphicChar(None, colors.GRAY, icon.HEART)
            self.target_entity.char_printer.append_graphic_char_temporary_frames([gray_heart])
            self.send_message()
        self.tick(time_spent)

    def _on_remove_effect(self):
        self.target_entity.health_modifier.kill()


class StatusAdder(EntityEffect):
    def __init__(self, source_entity, status_flag, time_to_live=1):
        super(StatusAdder, self).__init__(source_entity, time_to_live,
                                          EffectTypes.STATUS_ADDER)
        self.status_flag = status_flag

    def update(self, time_spent):
        status_flags = StatusFlags([self.status_flag])
        status_flags.to_be_removed = True
        self.target_entity.set_child(status_flags)
        self.tick(time_spent)


class Teleport(EntityEffect):
    def __init__(self, source_entity, time_to_live=1):
        super(Teleport, self).__init__(source_entity, time_to_live, EffectTypes.TELEPORT)

    def update(self, time_spent):
        positions = (self.target_entity.dungeon_level.value.
                     get_walkable_positions(self.target_entity,
                                            self.target_entity.position.value))
        random_positions = random.sample(positions, len(positions))

        for position in random_positions:
            teleport_successful = self.target_entity.mover.try_move(position)
            if teleport_successful:
                self.target_entity.game_state.value.dungeon_needs_redraw = True
                break
        self.tick(time_spent)


class AttackEntityEffect(EntityEffect):
    def __init__(self, source_entity, damage, damage_types, hit, hit_message=messenger.HIT_MESSAGE,
                 miss_message=messenger.MISS_MESSAGE, no_stack_id=None, time_to_live=1,
                 target_entity_effects=[]):
        super(AttackEntityEffect, self).__init__(source_entity=source_entity,
                                                 effect_type=EffectTypes.DAMAGE,
                                                 no_stack_id=no_stack_id,
                                                 time_to_live=time_to_live)
        self.hit = hit
        self.damage = damage
        self.damage_types = damage_types
        self.miss_message = miss_message
        self.hit_message = hit_message
        self.target_entity_effects = target_entity_effects

    def send_miss_message(self):
        messenger.msg.send_visual_message(self.miss_message % {"source_entity": self.source_entity.description.long_name,
                                                   "target_entity": self.target_entity.description.long_name},
                                          self.target_entity.position.value)

    def send_hit_message(self, damage_caused):
        source_entity_name = self.source_entity.description.long_name if self.source_entity else None
        target_entity_name = self.target_entity.description.long_name if self.target_entity else None
        m = self.hit_message % {"source_entity": source_entity_name,
                                "target_entity": target_entity_name,
                                "damage": str(damage_caused)}
        messenger.msg.send_visual_message(m, self.target_entity.position.value)

    def is_a_hit(self):
        return self.target_entity.dodger.is_a_hit(self.hit)

    def hit_target(self):
        self.add_effects_to_target()
        damage_after_armor = self.target_entity.armor_checker.get_damage_after_armor(self.damage, self.damage_types)
        damage_after_resist = self.target_entity.resistance_checker.get_damage_after_resistance(damage_after_armor, self.damage_types)
        damage_caused = self.target_entity.health_modifier.hurt(damage_after_resist, entity=self.source_entity)
        return damage_caused

    def update(self, time_spent):
        if self.target_entity.resistance_checker.is_immune(self.damage_types):
            pass
        elif self.is_a_hit():
            damage_caused = self.hit_target()
            self.send_hit_message(damage_caused)
        else:
            self.send_miss_message()
        self.tick(time_spent)

    def add_effects_to_target(self):
        for effect in self.target_entity_effects:
            self.target_entity.effect_queue.add(effect)


class UndodgeableAttackEntityEffect(AttackEntityEffect):
    def __init__(self, source_entity, damage, damage_types, hit_message=messenger.HIT_MESSAGE,
                 no_stack_id=None, time_to_live=1):
        super(UndodgeableAttackEntityEffect, self).__init__(source_entity, damage, damage_types, -1,
                                                            hit_message=hit_message,
                                                            no_stack_id=no_stack_id,
                                                            time_to_live=time_to_live)

    def is_a_hit(self):
        return True


class HealthRegain(EntityEffect):
    def __init__(self, source_entity, health, turn_interval, time_to_live, no_stack_id=None):
        super(HealthRegain, self).__init__(source_entity=source_entity, effect_type=EffectTypes.HEAL,
                                           no_stack_id=no_stack_id, time_to_live=time_to_live)
        self.health = health
        self.time_interval = turn_interval * gametime.single_turn
        self.time_until_next_heal = self.time_interval

    def update(self, time_spent):
        if self.time_until_next_heal <= 0:
            self.target_entity.health_modifier.heal(self.health)
            self.time_until_next_heal = self.time_interval
        self.time_until_next_heal -= time_spent
        self.tick(time_spent)


class DamageOverTimeEffect(EntityEffect):
    def __init__(self, source_entity, damage, damage_types, turn_interval, turns_to_live, damage_message, no_stack_id=None):
        super(DamageOverTimeEffect, self).__init__(source_entity=source_entity, effect_type=EffectTypes.DAMAGE,
                                                   no_stack_id=no_stack_id, time_to_live=turns_to_live * gametime.single_turn)
        self.damage = damage
        self.damage_types = damage_types
        self.time_interval = turn_interval * gametime.single_turn
        self.damage_message = damage_message
        self.time_until_next_damage = self.time_interval

    def send_damage_message(self, damage_caused):
        message_arguments = {}
        if self.source_entity and self.source_entity.has("description"):
            message_arguments["source_entity"] = self.source_entity.description.long_name
        if self.target_entity and self.target_entity.has("description"):
            message_arguments["target_entity"] = self.target_entity.description.long_name
        message_arguments["damage"] = str(damage_caused)
        m = self.damage_message % message_arguments
        messenger.msg.send_visual_message(m, self.target_entity.position.value)

    def damage_target(self):
        damage_after_armor = self.target_entity.armor_checker.get_damage_after_armor(self.damage, self.damage_types)
        damage_after_resist = self.target_entity.resistance_checker.get_damage_after_resistance(damage_after_armor, self.damage_types)
        damage_caused = self.target_entity.health_modifier.hurt(damage_after_resist, entity=self.source_entity,
                                                                damage_types=self.damage_types)
        return damage_caused

    def update(self, time_spent):
        if (self.time_until_next_damage <= 0 and
                not self.target_entity.resistance_checker.is_immune(self.damage_types)):
            damage_caused = self.damage_target()
            self.send_damage_message(damage_caused)
            self.time_until_next_damage = self.time_interval
        self.time_until_next_damage -= time_spent
        self.tick(time_spent)


class UndodgeableDamagAndBlockSameEffect(EntityEffect):
    def __init__(self, source_entity, damage, damage_types, damage_message, no_stack_id, time_to_live):
        super(UndodgeableDamagAndBlockSameEffect, self).__init__(source_entity=source_entity,
                                                                 effect_type=EffectTypes.DAMAGE,
                                                                 time_to_live=time_to_live,
                                                                 no_stack_id=no_stack_id)
        self.damage = damage
        self.damage_types = damage_types
        self.damage_message = damage_message

    def send_damage_message(self, damage_caused):
        messenger.msg.send_visual_message(self.damage_message % {"source_entity": self.source_entity.description.long_name,
                                                     "target_entity": self.target_entity.description.long_name,
                                                     "damage": str(damage_caused)},
                                          self.target_entity.position.value)

    def update(self, time_spent):
        if (self.time_alive == 0 and
                not self.target_entity.resistance_checker.is_immune(self.damage_types)):
            damage_after_armor = self.target_entity.armor_checker.get_damage_after_armor(self.damage, self.damage_types)
            damage_after_resist = self.target_entity.resistance_checker.get_damage_after_resistance(damage_after_armor, self.damage_types)
            damage_caused = self.target_entity.health_modifier.hurt(damage_after_resist, entity=self.source_entity)
            self.send_damage_message(damage_caused)
        self.tick(time_spent)


class Heal(EntityEffect):
    def __init__(self, source_entity, health, heal_message=messenger.HEAL_MESSAGE, time_to_live=1):
        super(Heal, self).__init__(source_entity=source_entity,
                                   effect_type=EffectTypes.HEAL,
                                   time_to_live=time_to_live)
        self.health = health
        self.heal_message = heal_message

    def message(self):
        messenger.msg.send_visual_message(self.heal_message % {"source_entity": self.source_entity.description.long_name,
                                                   "target_entity": self.target_entity.description.long_name,
                                                   "health": str(self.health)},
                                          self.target_entity.position.value)

    def update(self, time_spent):
        self.target_entity.health_modifier.heal(self.health)
        self.message()
        self.tick(time_spent)


class AddSpoofChild(EntityEffect):
    def __init__(self, source_entity, spoof_child, time_to_live, no_stack_id=None):
        super(AddSpoofChild, self).__init__(source_entity=source_entity,
                                            effect_type=EffectTypes.ADD_SPOOF_CHILD,
                                            time_to_live=time_to_live,
                                            no_stack_id=no_stack_id)
        self.spoof_child = spoof_child

    def update(self, time_spent):
        self.target_entity.add_spoof_child(self.spoof_child)
        self.tick(time_spent)


class Equip(EntityEffect):
    def __init__(self, source_entity, item, equip_message=messenger.EQUIP_MESSAGE):
        super(Equip, self).__init__(source_entity=source_entity,
                                    effect_type=EffectTypes.EQUIPMENT,
                                    time_to_live=1)
        self.item = item
        self.equip_message = equip_message

    def message(self):
        messenger.msg.send_visual_message(self.equip_message % {"source_entity": self.source_entity.description.long_name,
                                                                "target_entity": self.target_entity.description.long_name,
                                                                "item": self.item.description.long_name},
                                          self.target_entity.position.value)

    def update(self, time_spent):
        equipment = self.queue.target_entity.equipment
        equip_succeeded = equipment.try_equip(self.item)
        if equip_succeeded:
            self.message()
            if self.queue.target_entity.inventory.has_item(self.item):
                self.queue.target_entity.inventory.remove_item(self.item)
        self.tick(time_spent)


class StepEffect(EntityEffect):
    def __init__(self, source_entity, item):
        super(StepEffect, self).__init__(source_entity=source_entity,
                                         effect_type=EffectTypes.EQUIPMENT,
                                         time_to_live=1)
        self.item = item

    def update(self, time_spent):
        pass


class Unequip(EntityEffect):
    def __init__(self, source_entity, equipment_slot):
        super(Unequip, self).__init__(source_entity=source_entity,
                                      effect_type=EffectTypes.EQUIPMENT,
                                      time_to_live=1)
        self.item = source_entity.equipment.get(equipment_slot)
        self.equipment_slot = equipment_slot
        self.unequip_message = messenger.UNEQUIP_MESSAGE

    def message(self):
        messenger.msg.send_visual_message(self.unequip_message % {"source_entity": self.source_entity.description.long_name,
                                                      "target_entity": self.target_entity.description.long_name,
                                                      "item": self.item.description.long_name},
                                          self.target_entity.position.value)

    def update(self, time_spent):
        equipment = self.target_entity.equipment
        if equipment.can_unequip_to_inventory(self.equipment_slot):
            underlip_succeeded =  equipment.unequip_to_inventory(self.equipment_slot)
            if underlip_succeeded:
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
        message = "%s equips %s." % (self.source_entity.description.long_name,
                                     self.item.description.long_name)
        messenger.msg.send_visual_message(message,
                                          self.target_entity.position.value)

    def update(self, time_spent):
        old_item = None
        if self.source_entity.equipment.slot_is_equiped(self.equipment_slot):
            old_item = self.source_entity.equipment.unequip(self.equipment_slot)

        equipment = self.target_entity.equipment
        equip_succeeded = equipment.try_equip(self.item)
        if equip_succeeded:
            self.message()
            self._item_flash_animation(self.target_entity, self.item)
            if self.source_entity.inventory.has_item(self.item):
                self.source_entity.inventory.remove_item(self.item)

        if not old_item is None:
            self.source_entity.inventory.try_add(old_item)
        self.tick(time_spent)

    def _item_flash_animation(self, entity, item):
        entity.char_printer.append_graphic_char_temporary_frames([item.graphic_char])
