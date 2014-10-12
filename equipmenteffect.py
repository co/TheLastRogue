import random
from Status import BLEED_STATUS_DESCRIPTION, LIFE_STEAL_STATUS_DESCRIPTION
from actor import StunnedActor
from attacker import DamageType, DamageTypes
import colors
from compositecommon import PoisonEntityEffectFactory, AddEffectToOtherSeenEntities, HealAnEntityOnDeath
from compositecore import Leaf
import entityeffect
import gametime
import geometry
import messenger
from mover import RandomStepper
from stats import DataTypes, DataPointBonusSpoof, DataPoint


class AttackEffect(Leaf):
    def __init__(self, effect_chance):
        super(AttackEffect, self).__init__()
        self.tags.add("attack_effect")
        self.effect_chance = effect_chance

    def roll_to_hit(self):
        return random.random() < self.effect_chance

    def attack_effect(self, source_entity, target_entity):
        pass


class AttackEffectWithItemStat(AttackEffect):
    def __init__(self, effect_chance):
        super(AttackEffectWithItemStat, self).__init__(effect_chance)
        self.tags.add("equipped_effect")

    def equipped_effect(self, entity):
        self.parent.add_spoof_child(self._item_stat())
        self._equipped_effect(entity)

    def _equipped_effect(self, entity):
        pass

    def first_tick(self, time):
        self.parent.add_spoof_child(self._item_stat())
        self._first_tick(time)

    def _first_tick(self, time):
        pass

    def _item_stat(self):
        return None


class BeforeAttackEffect(Leaf):
    TAG = "before_attack_effect"

    def __init__(self, effect_chance):
        super(BeforeAttackEffect, self).__init__()
        self.effect_chance = effect_chance
        self.tags.add(BeforeAttackEffect.TAG)

    def roll_to_hit(self):
        return random.random() < self.effect_chance

    def before_attack_effect(self, source_entity, target_entity):
        pass


class StunAttackEffect(AttackEffectWithItemStat):
    def __init__(self, effect_chance):
        super(StunAttackEffect, self).__init__(effect_chance)
        self.effect_chance = effect_chance
        self.component_type = "stun_attack_effect"

    def attack_effect(self, source_entity, target_entity):
        return target_entity.effect_queue.add(entityeffect.AddSpoofChild(source_entity, StunnedActor(),
                                                                         gametime.single_turn))

    def _item_stat(self):
        return ItemStat("Stun", self.effect_chance, colors.CHAMPAGNE, "Stun",
                        ItemStat.PERCENT_FORMAT, order=20, is_common_stat=False)


class TripAttackEffect(AttackEffectWithItemStat):
    def __init__(self, effect_chance):
        super(TripAttackEffect, self).__init__(effect_chance)
        self.effect_chance = effect_chance
        self.component_type = "trip_attack_effect"

    def attack_effect(self, source_entity, target_entity):
        return target_entity.effect_queue.add(entityeffect.AddSpoofChild(source_entity, RandomStepper(),
                                                                         gametime.single_turn))

    def _item_stat(self):
        return ItemStat("trip", self.effect_chance, colors.YELLOW, "Trip",
                        ItemStat.PERCENT_FORMAT, order=20, is_common_stat=False)


class ExtraSwingAttackEffect(AttackEffectWithItemStat):
    def __init__(self, effect_chance):
        super(ExtraSwingAttackEffect, self).__init__(effect_chance)
        self.effect_chance = effect_chance
        self.component_type = "extra_swing_attack_effect"

    def attack_effect(self, source_entity, target_entity):
        source_entity.melee_attacker.try_hit(target_entity)

    def _item_stat(self):
        return ItemStat("extra_swing", self.effect_chance, colors.LIGHT_BLUE, "Extra Swing",
                        ItemStat.PERCENT_FORMAT, order=10, is_common_stat=False)


class EquippedEffect(Leaf):
    """
    Parent items with this component has a
    effect that happens while item is equipped.
    """

    def __init__(self):
        super(EquippedEffect, self).__init__()
        self.tags.add("equipped_effect")

    def equipped_effect(self, entity):
        pass


class StatBonusEquipEffect(EquippedEffect):
    def __init__(self, stat, bonus):
        super(StatBonusEquipEffect, self).__init__()
        self.component_type = "equip_stat_bonus_effect_" + stat
        self.stat = stat
        self.bonus = bonus

    def equipped_effect(self, entity):
        """
        Causes the entity that equips this have a bonus to one stat.
        """
        entity.add_spoof_child(DataPointBonusSpoof(self.stat, self.bonus))
        self._equipped_effect(entity)

    def _equipped_effect(self, entity):
        pass


class StatBonusEquipEffectWithItemStat(StatBonusEquipEffect):
    def __init__(self, stat, bonus):
        super(StatBonusEquipEffectWithItemStat, self).__init__(stat, bonus)

    def equipped_effect(self, entity):
        """
        Causes the entity that equips this have a bonus to one stat.
        """
        entity.add_spoof_child(DataPointBonusSpoof(self.stat, self.bonus))
        self.parent.add_spoof_child(self._item_stat())
        self._equipped_effect(entity)

    def _equipped_effect(self, entity):
        pass

    def first_tick(self, time):
        self.parent.add_spoof_child(self._item_stat())
        self._first_tick(time)

    def _first_tick(self, time):
        pass

    def _item_stat(self):
        return None


class CounterAttackEffect(StatBonusEquipEffectWithItemStat):
    def __init__(self, effect_chance):
        super(CounterAttackEffect, self).__init__(DataTypes.COUNTER_ATTACK_CHANCE, effect_chance)
        self.effect_chance = effect_chance
        self.component_type = "counter_attack"

    def _item_stat(self):
        return ItemStat("counter_attack_weapon_effect", self.effect_chance, colors.PURPLE, "Counter",
                        ItemStat.PERCENT_FORMAT, order=30, is_common_stat=False)


class IgnoreArmorAttackEffect(BeforeAttackEffect):
    def __init__(self, effect_chance):
        super(IgnoreArmorAttackEffect, self).__init__(effect_chance)
        self.component_type = "ignore_armor_attack"
        self.tags.add("equipped_effect")

    def before_attack_effect(self, source_entity, target_entity):
        self.parent.add_spoof_child(DamageType(DamageTypes.IGNORE_ARMOR))

    def equipped_effect(self, entity):
        self.parent.add_spoof_child(self._item_stat())

    def _item_stat(self):
        return ItemStat("ignore_armor_weapon_effect", self.effect_chance, colors.BLUE, "Ignore Armor",
                        ItemStat.PERCENT_FORMAT, order=30, is_common_stat=False)


class CritChanceBonusEffect(StatBonusEquipEffectWithItemStat):
    def __init__(self, effect_chance):
        super(CritChanceBonusEffect, self).__init__(DataTypes.CRIT_CHANCE, effect_chance)
        self.effect_chance = effect_chance
        self.component_type = "crit_chance_bonus"

    def _item_stat(self):
        return ItemStat("crit_chance_weapon_effect", self.effect_chance, colors.RED, "Crit %",
                        ItemStat.PERCENT_FORMAT, order=40, is_common_stat=True)


class OffenciveAttackEffect(StatBonusEquipEffectWithItemStat):
    def __init__(self, effect_chance):
        super(OffenciveAttackEffect, self).__init__(DataTypes.OFFENCIVE_ATTACK_CHANCE, effect_chance)
        self.effect_chance = effect_chance
        self.component_type = "offencive_attack"

    def _item_stat(self):
        return ItemStat(DataTypes.OFFENCIVE_ATTACK_CHANCE, self.effect_chance, colors.LIGHT_GREEN, "Strike Step",
                        ItemStat.PERCENT_FORMAT, order=40, is_common_stat=False)


class DefenciveAttackEffect(StatBonusEquipEffectWithItemStat):
    def __init__(self, effect_chance):
        super(DefenciveAttackEffect, self).__init__(DataTypes.DEFENCIVE_ATTACK_CHANCE, effect_chance)
        self.effect_chance = effect_chance
        self.component_type = "defencive_attack"

    def _item_stat(self):
        return ItemStat(DataTypes.DEFENCIVE_ATTACK_CHANCE, self.effect_chance, colors.LIGHT_GREEN, "Def Strike",
                        ItemStat.PERCENT_FORMAT, order=40, is_common_stat=False)


class BleedAttackEffect(AttackEffectWithItemStat):
    def __init__(self, effect_chance):
        super(BleedAttackEffect, self).__init__(effect_chance)
        self.effect_chance = effect_chance
        self.component_type = "bleed_attack_effect"

    def attack_effect(self, source_entity, target_entity):
        turns = random.randrange(2, 6)
        damage_per_turn = 1
        damage_interval = 1
        bleed_effect = entityeffect.BleedEffect(source_entity, damage_per_turn, [DamageTypes.BLEED],
                                                damage_interval, turns,
                                                messenger.BLEED_MESSAGE, BLEED_STATUS_DESCRIPTION)
        target_entity.effect_queue.add(bleed_effect)

    def _item_stat(self):
        return ItemStat("bleed_weapon_effect", self.effect_chance, colors.RED, "Bleed",
                        ItemStat.PERCENT_FORMAT, order=30, is_common_stat=False)


class PoisonAttackEffect(AttackEffectWithItemStat):
    def __init__(self, effect_chance):
        super(PoisonAttackEffect, self).__init__(effect_chance)
        self.effect_chance = effect_chance
        self.component_type = "poison_attack_effect"

    def attack_effect(self, source_entity, target_entity):
        min_damage = 4
        max_damage = 8
        turn_interval = 2
        turns = 20
        factory = PoisonEntityEffectFactory(source_entity, random.randrange(min_damage, max_damage), turn_interval, turns)
        target_entity.effect_queue.add(factory())

    def _item_stat(self):
        return ItemStat("bleed_weapon_effect", self.effect_chance, colors.RED, "Bleed",
                        ItemStat.PERCENT_FORMAT, order=30, is_common_stat=False)


class KnockBackAttackEffect(AttackEffectWithItemStat):
    def __init__(self, effect_chance):
        super(KnockBackAttackEffect, self).__init__(effect_chance)
        self.effect_chance = effect_chance
        self.component_type = "knock_back_attack_effect"

    def attack_effect(self, source_entity, target_entity):
        knock_position = geometry.other_side_of_point(self.parent.position.value,
                                                      target_entity.position.value)
        target_entity.mover.try_move(knock_position)

    def _item_stat(self):
        return ItemStat("knock_back_weapon_effect", self.effect_chance, colors.CHAMPAGNE, "Knock Back",
                        ItemStat.PERCENT_FORMAT, order=25, is_common_stat=False)


class ItemStat(DataPoint):
    REGULAR_FORMAT = 0
    PERCENT_FORMAT = 1
    MULTIPLIER_FORMAT = 2
    RANGE_FORMAT = 3

    def __init__(self, component_type, value, color_fg, screen_name=None, formatting=REGULAR_FORMAT, order=50,
                 is_common_stat=True):
        super(ItemStat, self).__init__(component_type, value)
        self.tags.add("item_stat")
        self.color_fg = color_fg
        self.order = order
        if screen_name:
            self._screen_name = screen_name
        else:
            self._screen_name = component_type
        self.format = formatting
        self.is_common_stat = is_common_stat

    def get_value_text(self):
        if self.format == ItemStat.PERCENT_FORMAT:
            return "{:.0f}".format(self.value * 100) + "% "
        elif self.format == ItemStat.MULTIPLIER_FORMAT:
            return "x {:.1f}".format(self.value)
        else:
            return str(self.value) + "  "

    def get_text(self, width):
        return str(self._screen_name + self.get_value_text().rjust(width - len(self._screen_name)))


class RangeItemStat(ItemStat):
    def __init__(self, component_type, min_value, max_value, color_fg, screen_name=None,
                 order=50, is_common_stat=True):
        super(RangeItemStat, self).__init__(component_type, min_value, color_fg, screen_name=screen_name,
                                            formatting=ItemStat.REGULAR_FORMAT, order=order,
                                            is_common_stat=is_common_stat)
        self.min = min_value
        self.max = max_value

    def get_value_text(self):
        return str(self.min) + "-" + str(self.max) + "  "


class LifeStealEffect(EquippedEffect):
    def __init__(self):
        super(LifeStealEffect, self).__init__()
        self.component_type = "equipment_life_steal_effect"

    def equipped_effect(self, entity):
        """
        Causes seen entities to heal holder of this effect upon death.
        """
        effect = AddEffectToOtherSeenEntities(HealAnEntityDeathFactory(entity))
        entity.effect_queue.add(entityeffect.AddSpoofChild(entity, effect, 1))
        entity.effect_queue.add(entityeffect.StatusIconEntityEffect(entity, LIFE_STEAL_STATUS_DESCRIPTION,
                                                                    1, "life_steal_effect"))


class SetInvisibilityFlagEquippedEffect(EquippedEffect):
    def __init__(self):
        super(SetInvisibilityFlagEquippedEffect, self).__init__()
        self.component_type = "equipment_invisibility_effect"

    def equipped_effect(self, entity):
        """
        Causes the entity that equips this item to become invisible.
        """
        invisible_flag = entity.StatusFlags.INVISIBILE
        invisibility_effect = entityeffect.StatusAdder(self.parent, self.parent,
                                                       invisible_flag, time_to_live=1)
        self.parent.effect_queue.add(invisibility_effect)


class HealAnEntityDeathFactory(object):
    def __init__(self, entity):
        super(HealAnEntityDeathFactory, self).__init__()
        self.entity = entity

    def __call__(self):
        return HealAnEntityOnDeath(self.entity)