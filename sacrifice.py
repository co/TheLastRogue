from compositecore import Leaf, Composite
from stats import DataPointBonusSpoof, DataTypes
from text import Description


class Power(Composite):
    def __init__(self):
        super(Power, self).__init__()
        self.tags.add("power")
        self.buy_cost = 1

    def on_power_gained(self):
        self.parent.game_state.value.power_list.remove(self)


class NonPersistentPower(Power):
    def __init__(self):
        super(NonPersistentPower, self).__init__()
        self.tags.add("power")
        self.buy_cost = 1

    def on_tick(self, entity):
        self.parent.remove_component(self)


class StatPower(Power):
    """
    Abstract class, should never be gained by player.
    """
    def __init__(self):
        super(StatPower, self).__init__()

    def first_tick(self, time):
        """
        Causes the entity that equips this have a bonus to one stat.
        """
        self.parent.add_spoof_child(DataPointBonusSpoof(self.stat, self.bonus_value))


class StrengthPower(StatPower):
    def __init__(self):
        super(StrengthPower, self).__init__()
        self.component_type = "strength_power"
        self.buy_cost = 7
        self.set_child(Description("Bear's Strength", "You gain +2 Strength."))
        self.stat = DataTypes.STRENGTH
        self.bonus_value = 2


class StealthPower(StatPower):
    def __init__(self):
        super(StealthPower, self).__init__()
        self.component_type = "stealth_power"
        self.buy_cost = 6
        self.set_child(Description("Light Feet", "You gain +3 Stealth."))
        self.stat = DataTypes.STEALTH
        self.bonus_value = 3


class ArmorPower(StatPower):
    def __init__(self):
        super(ArmorPower, self).__init__()
        self.component_type = "armor_power"
        self.buy_cost = 9
        self.set_child(Description("Survivor", "You gain +1 armor."))
        self.stat = DataTypes.ARMOR
        self.bonus_value = 1


class CritPower(StatPower):
    def __init__(self):
        super(CritPower, self).__init__()
        self.component_type = "crit_power"
        self.buy_cost = 5
        self.set_child(Description("Cruel", "You have an extra 5% chance of inflicting a critical strike."))
        self.stat = DataTypes.CRIT_CHANCE
        self.bonus_value = 0.05


class FullHealPower(NonPersistentPower):
    def __init__(self):
        super(FullHealPower, self).__init__()
        self.component_type = "full_heal_power"
        self.buy_cost = 5
        self.set_child(Description("Full Heal", "You get fully healed at the cost of max health."))

    def on_power_gained(self):
        self.parent.health_modifier.heal(self.parent.health.hp.max_value)


def sacrifice_health(entity, cost):
    entity.health_modifier.decreases_max_hp(cost)


def new_power_list():
    return [FullHealPower(), StrengthPower(), StealthPower(), ArmorPower(), CritPower()]
