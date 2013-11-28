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
        if damage == 0 and rng.coin_flip():
            damage = 1  # You should never be completely safe
        if damage == 0:
            return damage
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

    def kill(self):
        """
        Removes all hp, this kills the entity.
        """
        self.parent.health.hp.set_min()


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

    def kill(self):
        """
        Removes all hp, this kills the entity.
        """
        self.next.kill()


class BlockDamageHealthSpoof(HealthSpoof):
    def __init__(self, block_amount, variance, blocked_damage_types):
        super(BlockDamageHealthSpoof, self).__init__()
        self.block_amount = block_amount
        self.variance = variance
        self.blocked_damage_types = set(blocked_damage_types)

    def hurt(self, damage, damage_types=[], entity=None):
        """
        Reduces damage done to parent entity.
        """
        block_amount = 0
        if len(set(damage_types) & self.blocked_damage_types) > 0:
            block_amount = rng.random_variance_no_negative(self.block_amount, self.variance)
        new_damage = max(damage - block_amount, 0)
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

        # Why does this key break the ratman!?
        #self.component_type = "bleed_when_damaged"

    def put_blood_on_tile(self, dungeon_level, position):
        terrain = dungeon_level.get_tile_or_unknown(position).get_terrain()
        if terrain.is_solid.value:
            terrain.graphic_char.color_fg = colors.RED
        else:
            spawner.spawn_blood_on_position(position, dungeon_level)

    def effect(self, damage, source_entity):
        dungeon_level = self.parent.dungeon_level.value
        if damage/float(self.parent.health.hp.max_value) > 0.2:
            self.put_blood_on_tile(dungeon_level, self.parent.position.value)

        if damage/float(self.parent.health.hp.max_value) > 0.4:
            point_behind = self._get_point_behind_unless_solid(source_entity.position.value, 1, dungeon_level)
            shape = shapegenerator.random_explosion_not_through_solid(point_behind, 2, dungeon_level)
            for point in shape:
                self.put_blood_on_tile(dungeon_level, point)

        if damage/float(self.parent.health.hp.max_value) > 0.8:
            point_behind = self._get_point_behind_unless_solid(source_entity.position.value, 2, dungeon_level)
            shape = shapegenerator.random_explosion_not_through_solid(point_behind, min(damage / 2, 7), dungeon_level)
            for point in shape:
                self.put_blood_on_tile(dungeon_level, point)

    def _get_point_behind_unless_solid(self, enemy_position, distance, dungeon_level):
        """
        Gets point right behind me seen from my enemy.
        """
        far_behind_point = geometry.sub_2d(self.parent.position.value, enemy_position)
        right_behind_point_delta = geometry.element_wise_round(geometry.normalize(far_behind_point))
        last_result = self.parent.position.value
        for _ in range(distance):
            result = geometry.add_2d(right_behind_point_delta, last_result)
            if position_is_solid(result, dungeon_level):
                return last_result
            last_result = result
        return result

def position_is_solid(position, dungeon_level):
    return dungeon_level.get_tile_or_unknown(position).get_terrain().is_solid.value
