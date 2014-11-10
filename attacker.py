import random
import action
import entityeffect
import geometry
import rng
from compositecore import Leaf, Composite
from stats import DataTypes, Flag, Tags
from trigger import Trigger, ON_ATTACKED_TRIGGER_TAG, STEP_NEXT_TO_ENEMY_TRIGGER_TAG, \
    ENEMY_STEPPING_NEXT_TO_ME_TRIGGER_TAG
from triggeredeffect import TriggeredEffect
from util import entity_stunned_turn


DEFAULT_CRIT_MULTIPLIER = 2


class AttackerBase(Leaf):
    def try_hit(self, entity):
        if not self.can_hit(entity):
            return False
        self.hit(entity)
        return True

    @property
    def accuracy(self):
        return self.parent.accuracy.value

    @property
    def min_damage(self):
        return self.parent.strength.value / 2

    @property
    def max_damage(self):
        return self.parent.strength.value / 2 + 3

    @property
    def crit_chance(self):
        return self.parent.unarmed_crit_chance.value

    @property
    def crit_multiplier(self):
        return DEFAULT_CRIT_MULTIPLIER

    def can_hit(self, entity):
        return True

    def hit(self, entity):
        self._on_hit(entity)
        self._before_attack_effects(entity)
        self._hit(entity)

    def _hit(self, entity):
        pass

    def _on_hit(self, entity):
        pass

    def _before_attack_effects(self, target_entity):
        for e in self.parent.get_children_with_tag("before_attack_effect"):
            e.before_attack_effect(self.parent, target_entity)


class WeaponAttacker(AttackerBase):
    def __init__(self, weapon):
        super(WeaponAttacker, self).__init__()
        self.weapon = weapon

    @property
    def accuracy(self):
        return self.weapon.accuracy.value

    @property
    def min_damage(self):
        return self.weapon.damage.min + self.parent.strength.value / 2

    @property
    def max_damage(self):
        return self.weapon.damage.max + self.parent.strength.value / 2

    @property
    def crit_chance(self):
        crit_chance = 0
        if self.parent.has(DataTypes.CRIT_CHANCE):
            crit_chance += self.parent.crit_chance.value
        if self.weapon.has(DataTypes.CRIT_CHANCE):
            crit_chance += self.weapon.crit_chance.value
        return crit_chance

    @property
    def crit_multiplier(self):
        if self.parent.has("crit_multiplier"):
            return self.parent.crit_multiplier.value
        return DEFAULT_CRIT_MULTIPLIER

    def attack_entity(self, target_entity, bonus_damage=0, bonus_hit=0):
        attack_effects = [effect for effect in self.weapon.get_children_with_tag("attack_effect")]
        damage_types = [effect.component_type for effect in self.parent.get_children_with_tag(Tags.DAMAGE_TYPE)]
        attack = Attack(self.min_damage, self.max_damage, damage_types, self.accuracy, crit_chance=self.crit_chance,
                        crit_multiplier=self.crit_multiplier, target_entity_effects=attack_effects)

        return attack.damage_entity(self.parent, target_entity, bonus_damage=bonus_damage, bonus_hit=bonus_hit)

    def _hit(self, target_entity):
        """
        Causes the entity to hit the target entity.
        """
        self.attack_entity(target_entity)


class WeaponRangedAttacker(WeaponAttacker):
    def __init__(self, weapon):
        super(WeaponRangedAttacker, self).__init__(weapon)
        self.component_type = "ranged_attacker"

    def can_hit(self, entity):
        return True


class WeaponMeleeAttacker(WeaponAttacker):
    def __init__(self, weapon):
        super(WeaponMeleeAttacker, self).__init__(weapon)
        self.component_type = "melee_attacker"

    def can_hit(self, entity):
        if geometry.chess_distance(self.parent.position.value, entity.position.value) > 1:
            return False
        return True


class UnarmedAttacker(AttackerBase):
    def __init__(self):
        super(UnarmedAttacker, self).__init__()
        self.component_type = "melee_attacker"

    @property
    def damage(self):
        damage_multiplier = 1
        if self.parent.has("throw_damage_multiplier"):
            damage_multiplier = self.parent.throw_damage_multiplier.value
        return int(2 * self.parent.strength.value * damage_multiplier / 3)

    def can_hit(self, entity):
        if geometry.chess_distance(self.parent.position.value, entity.position.value) > 1:
            return False

        # TODO This check should not be here!
        if entity is None or entity.faction.value == self.parent.faction.value:
            return False
        return True

    def _hit(self, target_entity):
        self._unarmed_damage().damage_entity(self.parent, target_entity)

    def _unarmed_damage(self):
        """
        Calculates an instance of damage
        caused by an unarmed hit by the entity.
        o
        """
        damage_types = [DamageTypes.BLUNT, DamageTypes.PHYSICAL]
        attack_effects = [effect for effect in self.parent.get_children_with_tag("attack_effect")]
        damage_min = self.damage
        damage_max = damage_min + 3
        return Attack(damage_min, damage_max, damage_types, self.accuracy,
                      crit_chance=self.crit_chance,
                      crit_multiplier=self.crit_multiplier,
                      target_entity_effects=attack_effects)


class ThrowRockAttacker(AttackerBase):
    def __init__(self):
        super(ThrowRockAttacker, self).__init__()
        self.component_type = "ranged_attacker"

    @property
    def damage(self):
        damage_multiplier = 1
        if self.parent.has("throw_damage_multiplier"):
            damage_multiplier = self.parent.throw_damage_multiplier.value
        return int(2 * self.parent.strength.value * damage_multiplier / 3)

    @property
    def accuracy(self):
        return self.parent.accuracy.value

    @property
    def crit_chance(self):
        return self.parent.unarmed_crit_chance.value

    @property
    def crit_multiplier(self):
        if self.parent.has("crit_multiplier"):
            return self.parent.crit_multiplier.value
        return DEFAULT_CRIT_MULTIPLIER

    def can_hit(self, entity):
        #TODO: faction test does not belong here!
        return not(entity is None or entity.faction.value == self.parent.faction.value)

    def _hit(self, target_entity):
        """
        Makes entity to hit the target entity with the force of a thrown rock.
        """
        damage_types = [DamageTypes.BLUNT, DamageTypes.PHYSICAL]
        damage_min = self.damage
        damage_max = 3
        thrown_damage = Attack(damage_min, damage_max, damage_types, self.accuracy,
                               crit_chance=self.crit_chance,
                               crit_multiplier=self.crit_multiplier)
        thrown_damage.damage_entity(self.parent, target_entity)


class PushBackAttacker(AttackerBase):
    """
    Component for attacking and checking if an attacking is legal. Attacks will cause Knock Back.
    """

    def __init__(self):
        super(PushBackAttacker, self).__init__()
        self.component_type = "melee_attacker"

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

    def is_a_hit(self, accuracy):
        """
        Returns true if it is a hit, false otherwise.
        """
        accuracy = max(accuracy, 1)
        evasion = max(self.parent.evasion.value, 1)
        return rng.stat_check(accuracy, evasion)


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
        armor = self.parent.armor.value
        if armor_will_block_attack(damage_types):
            if damage <= armor:
                damage_reduction = armor / 4
            else:
                damage_reduction = armor / 8
            if damage_reduction <= 0:
                return damage
            return max(damage - random.randrange(0, damage_reduction + 1), 0)
        return damage


def armor_will_block_attack(damage_types):
    return (not DamageTypes.IGNORE_ARMOR in damage_types) and (DamageTypes.BLUNT in damage_types or
                                                               DamageTypes.PIERCING in damage_types or
                                                               DamageTypes.CUTTING in damage_types)


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
    PHYSICAL = "physical_damage_type"
    MAGIC = "magic_damage_type"
    BLUNT = "blunt_damage_type"
    PIERCING = "piercing_damage_type"
    CUTTING = "cutting_damage_type"
    BLEED = "bleed_damage_type"
    ACID = "acid_damage_type"
    POISON = "poison_damage_type"
    LIGHTNING = "lightning_damage_type"
    FIRE = "fire_damage_type"
    REFLECT = "reflect_damage_type"

    IGNORE_ARMOR = "ignore_armor_damage_type"

    FALL = "fall_damage_type"


class DamageType(Flag):
    """
    Component which only has a component type. Composites with this component has this flag.
    """

    def __init__(self, damage_type):
        super(DamageType, self).__init__(damage_type)
        self.tags = Tags.DAMAGE_TYPE


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
    def __init__(self, damage_min, damage_max,
                 damage_types, accuracy, crit_chance=0, crit_multiplier=2, damage_multiplier=1, target_entity_effects=[]):
        self.damage_min = damage_min
        self.damage_max = damage_max
        self.damage_multiplier = damage_multiplier
        self.damage_types = damage_types
        self.accuracy = accuracy
        self.target_entity_effects = target_entity_effects
        self.crit_chance = crit_chance
        self.crit_multiplier = crit_multiplier

    def damage_entity(self, source_entity, target_entity, bonus_damage=0, bonus_hit=0, damage_multiplier=1):
        damage = calculate_damage(self.damage_min, self.damage_max, bonus_damage, damage_multiplier)
        damage_effect = entityeffect.AttackEntityEffect(source_entity, damage * self.damage_multiplier,
                                                        self.damage_types, self.accuracy + bonus_hit,
                                                        crit_chance=self.crit_chance,
                                                        crit_multiplier=self.crit_multiplier,
                                                        attack_effects=self.target_entity_effects)
        target_entity.effect_queue.add(damage_effect)


class UndodgeableAttack(object):
    def __init__(self, damage_min, damage_max, damage_types, damage_multiplier=1):
        self.damage_min = damage_min
        self.damage_max = damage_max
        self.damage_multiplier = damage_multiplier
        self.damage_types = damage_types

    def damage_entity(self, source_entity, target_entity, bonus_damage=0, damage_multiplier=1):
        damage = calculate_damage(self.damage_min, self.damage_max, bonus_damage, damage_multiplier)
        damage_effect = entityeffect.UndodgeableAttackEntityEffect(source_entity, damage * self.damage_multiplier,
                                                                   self.damage_types)
        target_entity.effect_queue.add(damage_effect)


def calculate_damage(damage_min, damage_max, bonus_damage, damage_multiplier):
    if damage_max < damage_min:
        return damage_min
    return (random.randrange(damage_min, damage_max + 1) + bonus_damage) * damage_multiplier


def set_counter_attack(entity):
    trigger_effect = Composite("counter_attack")
    trigger_effect.set_child(Trigger([ON_ATTACKED_TRIGGER_TAG]))
    trigger_effect.set_child(AttackEnemyTriggeredEffect(DataTypes.COUNTER_ATTACK_CHANCE))
    entity.set_child(trigger_effect)


def set_attack_enemy_i_step_next_to(entity):
    trigger_effect = Composite("attack_enemy_i_step_next_to")
    trigger_effect.set_child(Trigger([STEP_NEXT_TO_ENEMY_TRIGGER_TAG]))
    trigger_effect.set_child(AttackEnemyTriggeredEffect(DataTypes.OFFENCIVE_ATTACK_CHANCE))
    entity.set_child(trigger_effect)


def set_attack_enemy_stepping_next_to_me(entity):
    trigger_effect = Composite("set_attack_enemy_stepping_next_to_me")
    trigger_effect.set_child(Trigger([ENEMY_STEPPING_NEXT_TO_ME_TRIGGER_TAG]))
    trigger_effect.set_child(AttackEnemyTriggeredEffect(DataTypes.DEFENCIVE_ATTACK_CHANCE))
    entity.set_child(trigger_effect)


class AttackEnemyTriggeredEffect(TriggeredEffect):
    def __init__(self, entity_trigger_chance_attribute):
        super(AttackEnemyTriggeredEffect, self).__init__("attack_enemy_triggered_effect")
        self.entity_trigger_chance_attribute = entity_trigger_chance_attribute

    def trigger(self, **kwargs):
        source_entity = kwargs[action.SOURCE_ENTITY]
        target_entity = kwargs[action.TARGET_ENTITY]
        distance = geometry.chess_distance(source_entity.position.value, source_entity.position.value)
        if (distance <= 1 and source_entity.has(self.entity_trigger_chance_attribute) and
                    random.random() < source_entity.get_child(self.entity_trigger_chance_attribute).value):
            source_entity.melee_attacker.try_hit(target_entity)
