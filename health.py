from compositecore import Leaf
import counter
import colors
import geometry
import rng
import shapegenerator
import spawner


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
        self._call_damage_taken_effect(damage, entity)
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

    def _call_damage_taken_effect(self, damage, entity):
        """
        Calls all on damage taken effects.
        @param damage: The amount of damage taken.
        @param entity: The entity that caused the damage.
        """
        effects = self.parent.get_children_with_tag("damage_taken_effect")
        for effect in effects:
            effect.effect(damage, entity)


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


class DamageTakenEffect(Leaf):
    """
    Subclasses may define an effect that happens when parent takes damage.
    """
    def __init__(self):
        super(DamageTakenEffect, self).__init__()
        self.tags.add("damage_taken_effect")

    def effect(self, damage, source_entity):
        pass


class BleedWhenDamaged(DamageTakenEffect):
    """
    When parent takes damage, it will bleed pools of blood on the terrain.
    """
    def __init__(self):
        super(BleedWhenDamaged, self).__init__()
        self.component_type = "bleed_on_damaged"

        # dictionary collision!?
        #self.component_type = "bleed_when_damaged"

    def effect(self, damage, source_entity):
        dungeon_level = self.parent.dungeon_level.value
        if damage/float(self.parent.health.hp.max_value) > 0.2:
            spawner.spawn_blood_on_position(self.parent.position.value, dungeon_level)

        if damage/float(self.parent.health.hp.max_value) > 0.4:
            point_behind = self._get_point_behind(source_entity.position.value, 1)
            shape = shapegenerator.random_explosion(point_behind, 3)
            for point in shape:
                spawner.spawn_blood_on_position(point, dungeon_level)

        if damage/float(self.parent.health.hp.max_value) > 0.8:
            point_behind = self._get_point_behind(source_entity.position.value, 2)
            shape = shapegenerator.random_explosion(point_behind, 8)
            for point in shape:
                spawner.spawn_blood_on_position(point, dungeon_level)

    def _get_point_behind(self, enemy_position, distance):
        """
        Gets point right behind me seen from my enemy.
        """
        far_behind_point = geometry.sub_2d(self.parent.position.value, enemy_position)
        right_behind_point_delta = geometry.element_wise_round(geometry.normalize(far_behind_point))
        result = self.parent.position.value
        for _ in range(distance):
            result = geometry.add_2d(right_behind_point_delta, result)
        return result
