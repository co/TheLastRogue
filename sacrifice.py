from compositecore import Composite
from stats import DataPointBonusSpoof, DataTypes
from text import Description


RANK_ZERO = 0
RANK_ONE = 1
RANK_TWO = 2
RANK_THREE = 3


def rank_to_string(rank):
    if rank == RANK_ZERO:
        return ""
    if rank == RANK_ONE:
        return "I"
    if rank == RANK_TWO:
        return "II"
    if rank == RANK_THREE:
        return "III"


class Power(Composite):
    def __init__(self, cost, rank):
        super(Power, self).__init__()
        self.tags.add("power")
        self.buy_cost = cost
        self.rank = rank

    @property
    def prereqs(self):
        return {}

    def on_power_gained(self):
        pass


class NonPersistentPower(Power):
    def __init__(self, cost):
        super(NonPersistentPower, self).__init__(cost, RANK_ZERO)
        self.tags.add("power")
        self.buy_cost = 1

    def on_tick(self, entity):
        self.parent.remove_component(self)


class StatPower(Power):
    """
    Abstract class, should never be gained by player.
    """

    def __init__(self, stat, bonus_value, cost, rank):
        super(StatPower, self).__init__(cost, rank)
        self.stat = stat
        self.bonus_value = bonus_value

    @property
    def prereqs(self):
        if self.rank >= 2:
            return {
                self.component_type: self.rank - 1
            }
        return {}

    def first_tick(self, time):
        """
        Causes the entity that equips this have a bonus to one stat.
        """
        self.parent.add_spoof_child(DataPointBonusSpoof(self.stat, self.bonus_value))


class StrengthPower(StatPower):
    def __init__(self, bonus_value, cost, rank):
        super(StrengthPower, self).__init__(DataTypes.STRENGTH, bonus_value, cost, rank)
        self.component_type = "strength_power"
        self.set_child(Description("Brute " + rank_to_string(rank), "You gain +" + str(bonus_value) + " Strength."))


class StealthPower(StatPower):
    def __init__(self, bonus_value, cost, rank=RANK_ZERO):
        super(StealthPower, self).__init__(DataTypes.STEALTH, bonus_value, cost, rank)
        self.component_type = "stealth_power"
        self.set_child(Description("Light Feet " + rank_to_string(rank), "You gain +" + str(bonus_value) + " Stealth."))


class ArmorPower(StatPower):
    def __init__(self, bonus_value, cost, rank=RANK_ZERO):
        super(ArmorPower, self).__init__(DataTypes.ARMOR, bonus_value, cost, rank)
        self.component_type = "armor_power"
        self.set_child(Description("Hardened " + rank_to_string(rank), "You gain +" + str(bonus_value) + " Armor."))


class EvasionPower(StatPower):
    def __init__(self, bonus_value, cost, rank=RANK_ZERO):
        super(EvasionPower, self).__init__(DataTypes.EVASION, bonus_value, cost, rank)
        self.component_type = "evasion_power"
        self.set_child(Description("Acrobat " + rank_to_string(rank), "You gain +" + str(bonus_value) + " Evasion."))


class CritPower(StatPower):
    def __init__(self, bonus_value, cost, rank=RANK_ZERO):
        super(CritPower, self).__init__(DataTypes.CRIT_CHANCE, bonus_value, cost, rank)
        self.component_type = "crit_power"
        self.set_child(Description("Ruthless " + rank_to_string(rank),
                                   "You have an extra " + str( bonus_value) +
                                   "% chance of inflicting a critical strike."))


class FullHealPower(NonPersistentPower):
    def __init__(self):
        super(FullHealPower, self).__init__(cost=5)
        self.component_type = "full_heal_power"
        self.set_child(Description("Full Heal", "You get fully healed at the cost of max health."))

    def on_power_gained(self):
        self.parent.health_modifier.heal(self.parent.health.hp.max_value)


def sacrifice_health(entity, cost):
    entity.health_modifier.decreases_max_hp(cost)


def new_power_list():
    light_feet_power1 = StealthPower(3, 6, RANK_ONE)
    light_feet_power2 = StealthPower(6, 8, RANK_TWO)
    light_feet_power3 = StealthPower(9, 10, RANK_THREE)

    brute_power1 = StrengthPower(2, 7, RANK_ONE)
    brute_power2 = StrengthPower(4, 9, RANK_TWO)
    brute_power3 = StrengthPower(6, 11, RANK_THREE)

    hardened_power1 = ArmorPower(1, 8, RANK_ONE)
    hardened_power2 = ArmorPower(2, 10, RANK_TWO)
    hardened_power3 = ArmorPower(3, 12, RANK_THREE)

    ruthless_power1 = CritPower(0.05, 5, RANK_ONE)
    ruthless_power2 = CritPower(0.10, 7, RANK_TWO)
    ruthless_power3 = CritPower(0.15, 10, RANK_THREE)

    acrobat_power1 = EvasionPower(2, 8, RANK_ONE)
    acrobat_power2 = EvasionPower(4, 11, RANK_TWO)
    acrobat_power3 = EvasionPower(6, 14, RANK_THREE)

    return [
        FullHealPower(),
        brute_power1,
        brute_power2,
        brute_power3,

        light_feet_power1,
        light_feet_power2,
        light_feet_power3,

        hardened_power1,
        hardened_power2,
        hardened_power3,

        ruthless_power1,
        ruthless_power2,
        ruthless_power3,

        acrobat_power1,
        acrobat_power2,
        acrobat_power3,
        ]


def has_requirement_of_power(possible_power, current_powers):
    for required_type in possible_power.prereqs:
        if any(cp for cp in current_powers if cp.component_type == required_type):
            current_power = next(cp for cp in current_powers if cp.component_type == required_type)
            print "current", current_power.component_type, current_power.rank
            print "potent", possible_power.component_type, possible_power.rank
            if current_power.rank < possible_power.prereqs[required_type]:
                return False
        else:
            return False
    return True


def get_possible_powers(current_powers):
    return get_possible_powers_of_list(current_powers, new_power_list())


def get_possible_powers_of_list(current_powers, considered_powers):
    print considered_powers
    possible_powers = []
    for p in considered_powers:
        if any(power for power in current_powers if power.component_type == p.component_type and power.rank >= p.rank):
            continue
        print p.component_type, p.rank
        if has_requirement_of_power(p, current_powers):
            possible_powers.append(p)
    return possible_powers

