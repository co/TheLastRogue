import rng
import entityeffect


class DamageTypes(object):
    PHYSICAL = 0
    MAGIC = 1
    BLUNT = 2
    PIERCING = 3
    CUTTING = 4
    ACID = 5


class Damage(object):
    def __init__(self, strength, variance, damage_types, damage_multiplier=1):
        self.strength = strength
        self.variance = variance
        self.damage_multiplier = damage_multiplier
        self.damage_types = damage_types

    def damage_entity(self, source_entity, target_entity):
        damage = rng.random_variance_no_negative(self.strength, self.variance)
        damage_effect =\
            entityeffect.DamageEntityEffect(source_entity,
                                            damage * self.damage_multiplier,
                                            self.damage_types)
        target_entity.effect_queue.add(damage_effect)
