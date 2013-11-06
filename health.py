from compositecore import Leaf
import counter
import colors
import rng


class Health(Leaf):
    """
    Health Component. Composites holding this has health points.

    Attributes:
        _health_counter (Counter): Holds the min, max and current health.
    """
    def __init__(self, max_hp):
        super(Health, self).__init__()
        self.component_type = "health"
        self.hp = counter.Counter(max_hp, max_hp)
        self.killer = None

    def is_dead(self):
        """
        Returns True if the entity is considered dead.
        """
        return self.hp.value == 0


class HealthModifier(Leaf):
    def __init__(self):
        super(HealthModifier, self).__init__()
        self.component_type = "health_modifier"

    def hurt(self, damage, damage_types=[], entity=None):
        """
        Damages the entity by reducing hp by damage.
        """
        self.parent.health.hp.decrease(damage)
        self._animate_hurt()
        if self.parent.health.is_dead():
            self.parent.health.killer = entity
        return damage

    def _animate_hurt(self):
        """
        Adds a blink animation to hurt entity.
        """
        self.parent.char_printer.append_fg_color_blink_frames([colors.LIGHT_PINK,
                                                               colors.RED])

    def heal(self, health):
        """
        Heals increases the current hp by health.
        """
        self.parent.health.hp.increase(health)
        return health

    def increases_max_hp(self, amount):
        """
        Increases max hp and heals the same amount.
        """
        hp = self.parent.health.hp
        hp.max_value = hp.max_value + amount
        hp.increase(amount)


class HealthSpoof(Leaf):
    def __init__(self):
        super(HealthSpoof, self).__init__()
        self.component_type = "health_modifier"

    def hurt(self, damage, damage_types=[], entity=None):
        """
        Passes call to next spoof.
        """
        return self.next.hurt(damage, damage_types=damage_types, entity=entity)

    def heal(self, health):
        """
        Passes call to next spoof.
        """
        return self.next.heal(health)

    def increases_max_hp(self, amount):
        """
        Passes call to next spoof.
        """
        return self.next.increases_max_hp(amount)


class BlockDamageHealthSpoof(HealthSpoof):
    def __init__(self, block_ammount, variance, blocked_damage_types):
        super(BlockDamageHealthSpoof, self).__init__()
        self.block_ammount = block_ammount
        self.variance = variance
        self.blocked_damage_types = set(blocked_damage_types)

    def hurt(self, damage, damage_types=[], entity=None):
        """
        Reduces damage done to parent entity.
        """
        block_ammount = 0
        if(len(set(damage_types) & self.blocked_damage_types) > 0):
            block_ammount = rng.random_variance(self.block_ammount,
                                                self.variance)
        new_damage = max(damage - block_ammount, 0)
        return self.next.hurt(new_damage, damage_types=damage_types,
                              entity=entity)
