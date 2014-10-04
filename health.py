import logging
from Status import DAMAGE_REFLECT_STATUS_DESCRIPTION
from attacker import DamageTypes
from compositecore import Leaf
import counter
import colors
from dungeontrash import PoolOfBlood
import entityeffect
import geometry
from graphic import GraphicChar
import icon
import rng
import settings
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

    def is_damaged(self):
        """
        Returns True if the entity is considered dead.
        """
        return self.hp.value != self.hp.max_value


class HealthModifier(Leaf):
    def __init__(self):
        super(HealthModifier, self).__init__()
        self.component_type = "health_modifier"

    def hurt(self, damage, entity=None, damage_types=[]):
        """
        Damages the entity by reducing hp by damage.
        """
        if damage == 0 and rng.coin_flip():
            damage = 1  # You should never be completely safe
        if damage == 0:
            return damage
        self.parent.health.hp.decrease(damage)
        self._animate_hurt(damage_types)
        if self.parent.health.is_dead():
            self.parent.health.killer = entity
        self._call_damage_taken_effect(damage, entity, damage_types)
        return damage

    def _animate_hurt(self, damage_types):
        """
        Adds a blink animation to hurt entity.
        """
        frame_length = max(settings.ANIMATION_DELAY / 2, 1)
        hurt_colors = self._get_hurt_colors(damage_types)
        self.parent.char_printer.append_fg_color_blink_frames(hurt_colors, frame_length)

    def _get_hurt_colors(self, damage_types):
        if DamageTypes.POISON in damage_types:
            return [colors.GREEN, colors.GREEN_D]
        return [colors.LIGHT_PINK, colors.RED]

    def heal(self, health):
        """
        Heals increases the current hp by health.
        """
        if not self.parent.health.hp.value == self.parent.health.hp.max_value:
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

    def decreases_max_hp(self, amount):
        """
        Decreases max hp and heals the same amount.
        """
        hp = self.parent.health.hp
        hp.max_value = hp.max_value - amount
        hp.value = min(hp.value, hp.max_value)

    def _animate_max_hp_gain(self):
        heart_graphic_char = GraphicChar(None, colors.CYAN, icon.HEALTH_GAIN_ICON)
        self.parent.char_printer.append_graphic_char_temporary_frames([heart_graphic_char])

    def _call_damage_taken_effect(self, damage, entity, damage_types):
        """
        Calls all on damage taken effects.
        @param damage: The amount of damage taken.
        @param entity: The entity that caused the damage.
        """

        effects = self.parent.get_children_with_tag("damage_taken_effect")
        for effect in effects:
            effect.effect(damage, entity, damage_types)

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

    def effect(self, damage, source_entity, damage_types=[]):
        pass


class ReflectDamageTakenEffect(DamageTakenEffect):
    def __init__(self):
        super(ReflectDamageTakenEffect, self).__init__()
        self.component_type = "reflect_damage"
        self.damage = 1

    def effect(self, damage, source_entity, damage_types=[]):
        if (damage >= 1 and
                source_entity and
                source_entity.has("health_modifier") and
                not DamageTypes.REFLECT in damage_types and
                source_entity != self.parent and
                rng.coin_flip()):
            damage_effect = entityeffect.UndodgeableAttackEntityEffect(self.parent, self.damage,
                                                                       [DamageTypes.MAGIC, DamageTypes.REFLECT])
            source_entity.effect_queue.add(damage_effect)
        if source_entity:
            source_entity.effect_queue.add(entityeffect.StatusIconEntityEffect(source_entity, DAMAGE_REFLECT_STATUS_DESCRIPTION, 1))


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
        elif not the_terrain.has("is_chasm"):
            spawn_blood_on_position(position, dungeon_level)

    def effect(self, damage, source_entity, damage_types=[]):
        dungeon_level = self.parent.dungeon_level.value
        is_bleed_damage = DamageTypes.BLEED in damage_types
        if damage / float(self.parent.health.hp.max_value) > 0.2 or is_bleed_damage:
            self.put_blood_on_tile(dungeon_level, self.parent.position.value)

        if damage / float(self.parent.health.hp.max_value) > 0.4:
            point_behind = self._get_point_behind_unless_solid(source_entity.position.value, 1, dungeon_level)
            shape = shapegenerator.random_explosion_not_through_solid(point_behind, 2, dungeon_level)
            for point in shape:
                self.put_blood_on_tile(dungeon_level, point)

        if damage / float(self.parent.health.hp.max_value) > 0.8:
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
    return dungeon_level.get_tile_or_unknown(position).get_terrain().has("is_solid")


def spawn_blood_on_position(position, dungeon_level):
    corpse = PoolOfBlood()
    spawn_succeded = corpse.mover.try_move(position, dungeon_level)
    if not spawn_succeded:
        logging.info("could not spawn pool of blood.")
        return False
    return True
