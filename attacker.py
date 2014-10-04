import random
import colors
import entityeffect
import geometry
import rng
from compositecore import Leaf
from equipment import EquipmentSlots
from stats import DataTypes
from util import entity_skip_turn, entity_stunned_turn


DEFAULT_CRIT_MULTIPLIER = 2


class Attacker(Leaf):
    """
    Component for attacking and checking if an attacking is legal.
    """

    def __init__(self):
        super(Attacker, self).__init__()
        self.component_type = "attacker"

    @property
    def actual_thrown_rock_damage(self):
        damage_multiplier = 1
        if self.parent.has("throw_damage_multiplier"):
            damage_multiplier = self.parent.throw_damage_multiplier.value
        return int(2 * self.parent.strength.value * damage_multiplier / 3)

    @property
    def thrown_rock_damage_variance(self):
        return int(self.actual_thrown_rock_damage / 2)

    @property
    def actual_thrown_hit(self):
        return self.parent.hit.value

    @property
    def actual_thrown_crit_chance(self):
        return self.parent.crit_chance.value

    @property
    def actual_thrown_crit_multiplier(self):
        if self.parent.has("crit_multiplier"):
            return self.parent.crit_multiplier.value
        return DEFAULT_CRIT_MULTIPLIER


    @property
    def actual_unarmed_damage(self):
        damage_multiplier = 1
        if self.parent.has("melee_damage_multiplier"):
            damage_multiplier = self.parent.melee_damage_multiplier.value
        return 1 + int(self.parent.strength.value * damage_multiplier) / 2

    @property
    def actual_unarmed_hit(self):
        return self.parent.hit.value

    @property
    def actual_unarmed_crit_chance(self):
        return self.parent.crit_chance.value

    @property
    def actual_unarmed_crit_multiplier(self):
        return self.actual_thrown_crit_multiplier

    def try_hit(self, position):
        """
        Tries to hit an entity at a position.

        Returns False if there is no entity
        there or the entity is of the same faction.
        """
        entity = (self.parent.dungeon_level.value.get_tile(position).get_first_entity())
        if (entity is None or
                    entity.faction.value == self.parent.faction.value):
            return False
        self.hit(entity)
        return True

    def throw_rock_damage_entity(self, target_entity):
        """
        Makes entity to hit the target entity with the force of a thrown rock.
        """
        damage_types = [DamageTypes.BLUNT, DamageTypes.PHYSICAL]
        thrown_damage = Attack(self.actual_thrown_rock_damage, self.thrown_rock_damage_variance,
                               damage_types, self.actual_thrown_hit, crit_chance=self.actual_thrown_crit_chance,
                               crit_multiplier=self.actual_thrown_crit_multiplier)
        thrown_damage.damage_entity(self.parent, target_entity)

    def hit(self, target_entity):
        """
        Causes the entity to hit the target entity.
        """
        equipment = self.parent.equipment
        self._on_hit(target_entity)
        if equipment.slot_is_equiped(EquipmentSlots.MELEE_WEAPON):
            weapon = self.parent.equipment.get(EquipmentSlots.MELEE_WEAPON)
            weapon.attack_provider.attack_entity(self.parent, target_entity)
        else:
            self._unarmed_damage().damage_entity(self.parent, target_entity)

    def _unarmed_damage(self):
        """
        Calculates an instance of damage
        caused by an unarmed hit by the entity.
        """
        damage_types = [DamageTypes.BLUNT, DamageTypes.PHYSICAL]

        target_entity_effects = [effect_factory_data_point.value() for effect_factory_data_point in
                                 self.parent.get_children_with_tag("unarmed_hit_target_entity_effect_factory")]
        damage_strength = self.actual_unarmed_damage
        return Attack(damage_strength, damage_strength / 4,
                      damage_types, self.actual_unarmed_hit, crit_chance=self.actual_unarmed_crit_chance,
                      crit_multiplier=self.actual_unarmed_crit_multiplier, target_entity_effects=target_entity_effects)

    def _on_hit(self, target_entity):
        pass


class KnockBackAttacker(Attacker):
    """
    Component for attacking and checking if an attacking is legal. Attacks will cause Knock Back.
    """

    def __init__(self):
        super(Attacker, self).__init__()
        self.component_type = "attacker"

    def _on_hit(self, target_entity):
        self._knock_away_entity(target_entity)

    def _knock_away_entity(self, target_entity):
        if rng.coin_flip():
            knock_position = geometry.other_side_of_point(self.parent.position.value,
                                                          target_entity.position.value)
            old_target_position = target_entity.position.value
            target_entity.mover.try_move(knock_position)
            self.parent.mover.try_move(old_target_position)
            if rng.coin_flip():
                entity_stunned_turn(self.parent, target_entity)


class Dodger(Leaf):
    """
    Component for calculating dodge.
    """

    def __init__(self):
        super(Dodger, self).__init__()
        self.component_type = "dodger"

    def is_a_hit(self, hit):
        """
        Returns true if it is a hit, false otherwise.
        """
        hit = max(hit, 1)
        evasion = max(self.parent.evasion.value, 1)
        return rng.stat_check(hit, evasion)


class ArmorChecker(Leaf):
    """
    Component for calculating dodge.
    """

    def __init__(self):
        super(ArmorChecker, self).__init__()
        self.component_type = "armor_checker"

    def get_damage_after_armor(self, damage, damage_types):
        """
        Returns the damage taken after it goes through the armor.
        """
        if (DamageTypes.BLUNT in damage_types or
                    DamageTypes.PIERCING in damage_types or
                    DamageTypes.CUTTING in damage_types):
            armor = self.parent.armor.value
            if damage <= armor:
                damage_reduction_mid = armor / 4
            else:
                damage_reduction_mid = armor / 8
            return max(damage - rng.random_variance_no_negative(damage_reduction_mid, damage_reduction_mid), 0)
        return damage


class ResistanceChecker(Leaf):
    """
    Component for calculating dodge.
    """

    def __init__(self):
        super(ResistanceChecker, self).__init__()
        self.component_type = "resistance_checker"

    def get_damage_after_resistance(self, damage, damage_types):
        """
        Returns the damage taken after it goes through the armor.
        """
        if self.is_immune(damage_types):
            return 0
        return damage

    def is_immune(self, damage_types):
        immunities = [component.immunity for component in self.parent.get_children_with_tag("immunity")]
        for immunity in immunities:
            if immunity in damage_types:
                return True
        return False


class DamageTypes(object):
    PHYSICAL = 0
    MAGIC = 1
    BLUNT = 2
    PIERCING = 3
    CUTTING = 4
    BLEED = 5
    ACID = 6
    POISON = 7
    FIRE = 8
    REFLECT = 9

    FALL = 10


class FireImmunity(Leaf):
    def __init__(self):
        super(FireImmunity, self).__init__()
        self.component_type = "fire_immunity"
        self.tags.add("immunity")
        self.immunity = DamageTypes.FIRE


class PoisonImmunity(Leaf):
    def __init__(self):
        super(PoisonImmunity, self).__init__()
        self.component_type = "poison_immunity"
        self.tags.add("immunity")
        self.immunity = DamageTypes.POISON


class Attack(object):
    def __init__(self, damage, variance,
                 damage_types, hit, crit_chance=0, crit_multiplier=2, damage_multiplier=1, target_entity_effects=[]):
        self.damage = damage
        self.variance = variance
        self.damage_multiplier = damage_multiplier
        self.damage_types = damage_types
        self.hit = hit
        self.target_entity_effects = target_entity_effects
        self.crit_chance = crit_chance
        self.crit_multiplier = crit_multiplier

    def damage_entity(self, source_entity, target_entity, bonus_damage=0, bonus_hit=0, damage_multiplier=1):
        damage = calculate_damage(self.damage, self.variance, bonus_damage, damage_multiplier)
        damage_effect = entityeffect.AttackEntityEffect(source_entity, damage * self.damage_multiplier,
                                                        self.damage_types, self.hit + bonus_hit,
                                                        crit_chance=self.crit_chance,
                                                        crit_multiplier=self.crit_multiplier,
                                                        attack_effects=self.target_entity_effects)
        target_entity.effect_queue.add(damage_effect)


class UndodgeableAttack(object):
    def __init__(self, damage, variance, damage_types, damage_multiplier=1):
        self.damage = damage
        self.variance = variance
        self.damage_multiplier = damage_multiplier
        self.damage_types = damage_types

    def damage_entity(self, source_entity, target_entity, bonus_damage=0, damage_multiplier=1):
        damage = calculate_damage(self.damage, self.variance, bonus_damage, damage_multiplier)
        damage_effect = entityeffect.UndodgeableAttackEntityEffect(source_entity, damage * self.damage_multiplier,
                                                                   self.damage_types)
        target_entity.effect_queue.add(damage_effect)


def calculate_damage(damage, damage_variance, bonus_damage, damage_multiplier):
    return rng.random_variance_no_negative((damage + bonus_damage) * damage_multiplier, damage_variance)


class OnAttackedEffect(Leaf):
    """
    Subclasses may define an effect that happens when parent takes damage.
    """

    def __init__(self):
        super(OnAttackedEffect, self).__init__()
        self.tags.add("on_attacked_effect")

    def effect(self, source_entity, damage_types=[]):
        pass


class CounterAttackOnDamageTakenEffect(OnAttackedEffect):
    def __init__(self):
        super(CounterAttackOnDamageTakenEffect, self).__init__()
        self.component_type = "counter_attack_on_damage_taken"
        self.damage = 1

    def effect(self, source_entity, damage_types=[]):
        distance = geometry.chess_distance(source_entity.position.value, self.parent.position.value)
        if (distance <= 1 and self.parent.has(DataTypes.COUNTER_ATTACK_CHANCE) and
                    random.random() < self.parent.counter_attack_chance.value):
            self.parent.attacker.hit(source_entity)
