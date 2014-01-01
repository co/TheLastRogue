import logging
from compositecore import Leaf
import counter
import colors
import dungeontrash
import geometry
from graphic import GraphicChar
import icon
import rng
import shapegenerator
import terrain


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

    def hurt(self, damage, entity=None):
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
        self._animate_heal()
        return health

    def _animate_heal(self):
        heart_graphic_char = GraphicChar(None, colors.RED, icon.HEALTH_GAIN_ICON)
        self.parent.char_printer.append_graphic_char_temporary_frames([heart_graphic_char])

    def increases_max_hp(self, amount):
        """
        Increases max hp and heals the same amount.
        """
        hp = self.parent.health.hp
        hp.max_value = hp.max_value + amount
        hp.increase(amount)
        self._animate_heal()
        self._animate_max_hp_gain()

    def _animate_max_hp_gain(self):
        heart_graphic_char = GraphicChar(None, colors.CYAN, icon.HEALTH_GAIN_ICON)
        self.parent.char_printer.append_graphic_char_temporary_frames([heart_graphic_char])

    def _call_damage_taken_effect(self, damage, entity):
        """
        Calls all on damage taken effects.
        @param damage: The amount of damage taken.
        @param entity: The entity that caused the damage.
        """
        effects = self.parent.get_children_with_tag("damage_taken_effect")
        for effect in effects:
            effect.effect(damage, entity)

    def kill(self, entity=None):
        """
        Removes all hp, this kills the entity.
        """
        if entity:
            self.parent.health.killer = entity
        self.parent.health.hp.set_min()


class HealthSpoof(Leaf):
    def __init__(self):
        super(HealthSpoof, self).__init__()
        self.component_type = "health_modifier"

    def hurt(self, damage, entity=None):
        """
        Passes call to next spoof.
        """
        return self.next.hurt(damage, entity=entity)

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
        the_terrain = dungeon_level.get_tile_or_unknown(position).get_terrain()
        if isinstance(the_terrain, terrain.Wall):
            the_terrain.graphic_char.color_fg = colors.RED
        else:
            spawn_blood_on_position(position, dungeon_level)

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


def spawn_blood_on_position(position, dungeon_level):
    corpse = dungeontrash.PoolOfBlood()
    spawn_succeded = corpse.mover.try_move(position, dungeon_level)
    if not spawn_succeded:
        logging.info("could not spawn pool of blood.")
        return False
    return True

