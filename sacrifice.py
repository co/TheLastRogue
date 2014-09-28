from compositecore import Leaf, Composite
from stats import DataPointBonusSpoof
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


class StrengthPower(Power):
    def __init__(self):
        super(StrengthPower, self).__init__()
        self.component_type = "strength_power"
        self.buy_cost = 7
        self.set_child(Description("Gain Strength", "You gain +2 Strength."))

    def first_tick(self, time):
        """
        Causes the entity that equips this have a bonus to one stat.
        """
        self.parent.add_spoof_child(DataPointBonusSpoof("strength", 2))


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
    return [FullHealPower(), StrengthPower()]
