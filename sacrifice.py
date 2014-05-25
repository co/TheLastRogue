from compositecore import Leaf


class Power(Leaf):
    def __init__(self):
        super(Power, self).__init__()
        self.tags.add("power")
        self.buy_cost = 1
        self.icon = "?"
        self.name = "_?_?_?"
        self.description = "??? ????? ? ??"

    def on_power_gained(self):
        pass


class NonPersistentPower(Power):
    def __init__(self):
        super(NonPersistentPower, self).__init__()
        self.tags.add("power")
        self.buy_cost = 1

    def on_tick(self, entity):
        self.parent.remove_component(self)


class FullHealPower(NonPersistentPower):
    def __init__(self):
        super(FullHealPower, self).__init__()
        self.component_type = "full_heal_power"
        self.buy_cost = 5
        self.icon = None
        self.name = "Full Heal"
        self.description = None

    def on_power_gained(self):
        self.parent.health_modifier.heal(self.parent.health.hp.max_value)


def sacrifice_health(entity, cost):
    entity.health_modifier.decreases_max_hp(cost)


power_list = [FullHealPower()]
