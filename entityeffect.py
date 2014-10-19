from audioop import add
import random
from animation import animate_point
import colors

from compositecore import Leaf
import gametime
from graphic import GraphicChar
import icon
import messenger
from statusflags import StatusFlags

# TODO: Idea replace effect types with spoofchildren and add time to live to spoof children.

# Effect types in execution order
class EffectTypes(object):
    EFFECT_REMOVER = 0
    STATUS_REMOVER = 1
    ADD_SPOOF_CHILD = 2
    REMOVE_CHILD = 3
    BLOCKER = 4
    STATUS_ADDER = 5
    TELEPORT = 6
    HEAL = 7
    UI = 8
    DAMAGE = 9
    EQUIPMENT = 10

    ALLTYPES = [EFFECT_REMOVER, STATUS_REMOVER, ADD_SPOOF_CHILD, REMOVE_CHILD, BLOCKER, STATUS_ADDER,
                TELEPORT, HEAL, UI, DAMAGE, EQUIPMENT]


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
        return self._effect_queue

    def add(self, effect):
        if effect.meld_id:
            if not any(effect.meld_id == e.meld_id for e in self.effects):
                self._add(effect)
            else:
                [e for e in self.effects][0].meld(effect)
        else:
            self._add(effect)

    def _add(self, effect):
        self._effect_queue[effect.effect_type].append(effect)
        effect.queue = self

    def remove(self, effect):
        self._effect_queue[effect.effect_type].remove(effect)
        effect.queue = None

    # TODO this is old lookup if can remove.
    def remove_status_adder_of_status(self, status_to_remove):
        for effect in self._effect_queue[EffectTypes.STATUS_ADDER]:
            if effect.status_flag == status_to_remove:
                self._effect_queue[EffectTypes.STATUS_ADDER].remove(effect)

    def update(self, time):
        for effect_type_queue in EffectTypes.ALLTYPES:
            for effect in self._effect_queue[effect_type_queue]:
                effect.update(time)


class EntityEffect(object):
    def __init__(self, source_entity, time_to_live, effect_type, meld_id=None, effect_id=None):
        self.source_entity = source_entity
        self.time_to_live = time_to_live
        self.effect_type = effect_type
        self.is_blocked = False
        self.meld_id = meld_id
        self.effect_id = effect_id
        self.queue = None
        self.time_alive = 0

    def update(self, time_spent):
        pass

    def meld(self, other_effect):
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


class EffectRemover(EntityEffect):
    def __init__(self, source_entity, effect_to_remove, time_to_live=1, message=None):
        super(EffectRemover, self).__init__(source_entity, time_to_live,
                                                  EffectTypes.EFFECT_REMOVER)
        self.the_message = message
        self.effect_to_remove = effect_to_remove

    def update(self, time_spent):
        removed_an_effect = False
        for index in range(len(self.queue.effects)):
            old_size = len(self.queue.effects[index])
            self.queue.effects[index] = [effect for effect in self.queue.effects[index]
                                         if not effect.effect_id == self.effect_to_remove]
            if not old_size == len(self.queue.effects[index]):
                removed_an_effect = True

        if removed_an_effect:
            self.message()
        self.tick(time_spent)

    def message(self):
        messenger.msg.send_visual_message(self.the_message % {"source_entity": self.source_entity.description.long_name,
                                                              "target_entity": self.target_entity.description.long_name},
                                          self.target_entity.position.value)


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
    def __init__(self, source_entity, damage, damage_types, accuracy, crit_chance=0, crit_multiplier=2,
                 hit_message=messenger.HIT_MESSAGE, miss_message=messenger.MISS_MESSAGE,
                 crit_message=messenger.CRIT_MESSAGE, hit_trigger_effect=[], meld_id=None, time_to_live=1,
                 attack_effects=[]):
        super(AttackEntityEffect, self).__init__(source_entity=source_entity,
                                                 effect_type=EffectTypes.DAMAGE,
                                                 meld_id=meld_id,
                                                 time_to_live=time_to_live)
        self.accuracy = accuracy
        self.damage = damage
        self.damage_types = damage_types
        self.miss_message = miss_message
        self.hit_message = hit_message
        self.attack_effects = attack_effects
        self.hit_trigger_effect = hit_trigger_effect
        self.crit_chance = crit_chance
        self.crit_multiplier = crit_multiplier
        self.crit_message = crit_message

    def send_miss_message(self):
        messenger.msg.send_visual_message(self.miss_message %
                                          {"source_entity": self.source_entity.description.long_name,
                                           "target_entity": self.target_entity.description.long_name},
                                          self.target_entity.position.value)

    def send_hit_message(self, message_template, damage_caused):
        source_entity_name = self.source_entity.description.long_name if self.source_entity else None
        target_entity_name = self.target_entity.description.long_name if self.target_entity else None
        m = message_template % {"source_entity": source_entity_name,
                                "target_entity": target_entity_name,
                                "damage": str(int(damage_caused))}
        messenger.msg.send_visual_message(m, self.target_entity.position.value)

    def is_a_hit(self):
        return self.target_entity.dodger.is_a_hit(self.accuracy) or self.target_entity.has("sleeping")

    def is_a_crit(self):
        return self.crit_chance > random.random() or self.target_entity.has("sleeping")

    def hit_target(self):
        is_crit = self.is_a_crit()
        damage = self.damage
        if is_crit:
            damage = self.damage * self.crit_multiplier
            animate_point(self.target_entity.game_state.value, self.target_entity.position.value,
                          [GraphicChar(None, colors.RED, "X")])
        damage_after_armor = self.target_entity.armor_checker.get_damage_after_armor(damage, self.damage_types)
        damage_after_resist = self.target_entity.resistance_checker.get_damage_after_resistance(damage_after_armor, self.damage_types)
        damage_caused = self.target_entity.health_modifier.hurt(damage_after_resist, entity=self.source_entity)
        self.execute_effects()
        if is_crit:
            self.send_hit_message(self.crit_message, damage_caused)
        else:
            self.send_hit_message(self.hit_message, damage_caused)

    def update(self, time_spent):
        if self.target_entity.resistance_checker.is_immune(self.damage_types):
            pass
        self.on_attacked_effects()
        if self.is_a_hit():
            self.hit_target()
        else:
            self.send_miss_message()
        self.tick(time_spent)

    def execute_effects(self):
        for effect in self.attack_effects:
            if effect.roll_to_hit():
                effect.attack_effect(self.source_entity, self.target_entity)

    def on_attacked_effects(self):
        for effect in self.target_entity.get_children_with_tag("on_attacked_effect"):
            effect.attacked_effect(self.source_entity, self.damage_types)


class UndodgeableAttackEntityEffect(AttackEntityEffect):
    def __init__(self, source_entity, damage, damage_types, hit_message=messenger.HIT_MESSAGE,
                 meld_id=None, time_to_live=1):
        super(UndodgeableAttackEntityEffect, self).__init__(source_entity, damage, damage_types, -1,
                                                            hit_message=hit_message,
                                                            meld_id=meld_id,
                                                            time_to_live=time_to_live)

    def is_a_hit(self):
        return True


class HealthRegain(EntityEffect):
    def __init__(self, source_entity, health, turn_interval, time_to_live, meld_id=None):
        super(HealthRegain, self).__init__(source_entity=source_entity, effect_type=EffectTypes.HEAL,
                                           meld_id=meld_id, time_to_live=time_to_live)
        self.health = health
        self.time_interval = turn_interval * gametime.single_turn
        self.time_until_next_heal = self.time_interval

    def update(self, time_spent):
        if self.time_until_next_heal <= 0:
            self.target_entity.health_modifier.heal(self.health)
            self.time_until_next_heal = self.time_interval
        self.time_until_next_heal -= time_spent
        self.tick(time_spent)


class StatusIconEntityEffect(EntityEffect):
    def __init__(self, source_entity, status_icon, time_to_live, meld_id=None):
        super(StatusIconEntityEffect, self).__init__(source_entity=source_entity, effect_type=EffectTypes.UI,
                                                     meld_id=meld_id, time_to_live=time_to_live)
        self.status_icon = status_icon

    def update(self, time_spent):
        if self.status_icon and self.target_entity.has("status_bar"):
            self.target_entity.status_bar.add(self.status_icon)
        self.tick(time_spent)


class DamageOverTimeEffect(EntityEffect):
    def __init__(self, source_entity, damage, damage_types, turn_interval, turns_to_live,
                 damage_message, status_icon=None, meld_id=None):
        super(DamageOverTimeEffect, self).__init__(source_entity=source_entity, effect_type=EffectTypes.DAMAGE,
                                                   meld_id=meld_id, time_to_live=turns_to_live * gametime.single_turn)
        self.damage = damage
        self.damage_types = damage_types
        self.time_interval = turn_interval * gametime.single_turn
        self.damage_message = damage_message
        self.time_until_next_damage = self.time_interval
        self.status_icon = status_icon

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

    def update_status_icon(self):
        if self.status_icon and self.target_entity.has("status_bar"):
            self.target_entity.status_bar.add(self.status_icon)

    def update(self, time_spent):
        if not self.target_entity.resistance_checker.is_immune(self.damage_types):
            if self.time_until_next_damage <= 0:
                damage_caused = self.damage_target()
                self.send_damage_message(damage_caused)
                self.time_until_next_damage = self.time_interval
            self.update_status_icon()
        self.time_until_next_damage -= time_spent
        self.tick(time_spent)


class BleedEffect(DamageOverTimeEffect):

    MAX_DAMAGE_PER_TURN = 3

    def __init__(self, source_entity, damage, damage_types, turn_interval, turns_to_live,
                 damage_message, status_icon):
        super(BleedEffect, self).__init__(source_entity, damage, damage_types, turn_interval, turns_to_live,
                                          damage_message, status_icon=status_icon, meld_id="bleed_effect")

    def meld(self, other_effect):
        self.time_to_live = max(other_effect.time_to_live, self.time_to_live)
        self.damage = min(self.damage + 1, BleedEffect.MAX_DAMAGE_PER_TURN)
        self.status_icon.graphic_char.icon = str(self.damage)


class UndodgeableDamagAndBlockSameEffect(EntityEffect):
    def __init__(self, source_entity, damage, damage_types,
                 damage_message, meld_id, status_icon=None, time_to_live=1):
        super(UndodgeableDamagAndBlockSameEffect, self).__init__(source_entity=source_entity,
                                                                 effect_type=EffectTypes.DAMAGE,
                                                                 time_to_live=time_to_live,
                                                                 meld_id=meld_id)
        self.damage = damage
        self.damage_types = damage_types
        self.damage_message = damage_message
        self.status_icon = status_icon

    def send_damage_message(self, damage_caused):
        messenger.msg.send_visual_message(self.damage_message % {"source_entity": self.source_entity.description.long_name,
                                                     "target_entity": self.target_entity.description.long_name,
                                                     "damage": str(damage_caused)},
                                          self.target_entity.position.value)

    def update(self, time_spent):
        if not self.target_entity.resistance_checker.is_immune(self.damage_types):
            if self.time_alive == 0:
                damage_after_armor = self.target_entity.armor_checker.get_damage_after_armor(self.damage, self.damage_types)
                damage_after_resist = self.target_entity.resistance_checker.get_damage_after_resistance(damage_after_armor, self.damage_types)
                damage_caused = self.target_entity.health_modifier.hurt(damage_after_resist, entity=self.source_entity)
                self.send_damage_message(damage_caused)
            self.update_status_icon()
        self.tick(time_spent)

    def update_status_icon(self):
        if self.status_icon and self.target_entity.has("status_bar"):
            self.target_entity.status_bar.add(self.status_icon)


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
    def __init__(self, source_entity, spoof_child, time_to_live, message_effect=None, meld_id=None, effect_id=None):
        super(AddSpoofChild, self).__init__(source_entity=source_entity,
                                            effect_type=EffectTypes.ADD_SPOOF_CHILD,
                                            time_to_live=time_to_live,
                                            meld_id=meld_id,
                                            effect_id=effect_id)
        self.message_effect = message_effect
        self.spoof_child = spoof_child

    def update(self, time_spent):
        self.target_entity.add_spoof_child(self.spoof_child)
        if self.message_effect:
            self.message()
        self.tick(time_spent)

    def message(self):
        messenger.msg.send_visual_message(self.message_effect % {"source_entity": self.source_entity.description.long_name,
                                                                 "target_entity": self.target_entity.description.long_name},
                                          self.target_entity.position.value)


class RemoveChildEffect(EntityEffect):
    def __init__(self, source_entity, component_type, time_to_live, meld_id=None):
        super(RemoveChildEffect, self).__init__(source_entity=source_entity,
                                                effect_type=EffectTypes.REMOVE_CHILD,
                                                time_to_live=time_to_live,
                                                meld_id=meld_id)
        self.component_type = component_type

    def update(self, time_spent):
        self.target_entity.remove_component_of_type(self.component_type)
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
            underlip_succeeded = equipment.unequip_to_inventory(self.equipment_slot)
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
