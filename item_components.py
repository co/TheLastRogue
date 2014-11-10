import random
from time import sleep

from Status import FROST_SLOW_STATUS_DESCRIPTION
from action import Action
import action
import animation
from attacker import DamageTypes, calculate_damage
from cloud import new_fire_cloud, new_explosion_cloud
import colors
from compositecommon import PoisonEntityEffectFactory, frost_effect_factory
from compositecore import Leaf
import direction
from dummyentities import dummy_flyer_open_doors
import entityeffect
import gametime
import geometry
from graphic import GraphicChar
import menufactory
from messenger import msg
import messenger
from monsteractor import TryPutToSleep
import rng
from shapegenerator import extend_points
from shoot import MissileHitDetection
from stats import DataPoint, DataTypes
from statusflags import StatusFlags
from terrain import GlassWall
from triggeredeffect import TriggeredEffect
import util


__author__ = 'co'


class ChooseChargeDeviceTriggeredEffect(TriggeredEffect):
    def __init__(self):
        super(ChooseChargeDeviceTriggeredEffect, self).__init__("choose_charge_device_triggered_effect")

    def can_trigger(self, **kwargs):
        print kwargs
        return kwargs[action.GAME_STATE].player.inventory.has_item_of_type(ItemType.DEVICE)

    def trigger(self, **kwargs):
        source_entity = kwargs[action.SOURCE_ENTITY]
        game_state = kwargs[action.GAME_STATE]
        callback = lambda item, source_entity=source_entity, **kwargs: self._charge_device(item, source_entity)
        choose_device_menu = menufactory.item_type_menu_callback_menu(source_entity,
                                                                      game_state.menu_prompt_stack,
                                                                      ItemType.DEVICE, "Device to Charge:", callback)
        game_state.start_prompt(choose_device_menu)

    def _charge_device(self, device, entity):
        device.charge.charges += 1
        entity.inventory.remove_one_item_from_stack(self.parent.item.value)


class DarknessTriggeredEffect(TriggeredEffect):
    def __init__(self):
        super(DarknessTriggeredEffect, self).__init__("darkness_triggered_effect")

    def trigger(self, **kwargs):
        ttl = gametime.single_turn * rng.random_variance(10, 5)
        source_entity = kwargs[action.SOURCE_ENTITY]
        entities = source_entity.dungeon_level.value.entities
        for entity in entities:
            sight_radius_spoof = DataPoint(DataTypes.SIGHT_RADIUS, 1)
            darkness_effect = entityeffect.AddSpoofChild(source_entity, sight_radius_spoof, time_to_live=ttl)
            entity.effect_queue.add(darkness_effect)


class WallToGlassTriggeredEffect(TriggeredEffect):
    def __init__(self):
        super(WallToGlassTriggeredEffect, self).__init__("wall_to_glass_triggered_effect")

    def trigger(self, **kwargs):
        source_entity = kwargs[action.SOURCE_ENTITY]
        sight_radius = source_entity.sight_radius.value
        dungeon_level = source_entity.dungeon_level.value
        top = source_entity.position.value[1] - sight_radius
        left = source_entity.position.value[0] - sight_radius
        turned_something_to_glass = False
        for x in range(left, left + 2 * sight_radius + 1):
            for y in range(top, top + 2 * sight_radius + 1):
                try:
                    turned_something_to_glass = self._turn_to_glass_if_wall((x, y), dungeon_level)
                    dungeon_level.signal_terrain_changed((x, y))
                except IndexError:
                    continue
        if turned_something_to_glass:
            msg.send_global_message(messenger.GLASS_TURNING_MESSAGE)

    def _turn_to_glass_if_wall(self, position, dungeon_level):
        terrain = dungeon_level.get_tile(position).get_terrain()
        if terrain.has("is_wall"):
            glass_wall = GlassWall()
            glass_wall.mover.replace_move(position, dungeon_level)
            return True
        return False


class SwapsTriggeredEffect(TriggeredEffect):
    def __init__(self):
        super(SwapsTriggeredEffect, self).__init__("swaps_glass_triggered_effect")

    def trigger(self, **kwargs):
        source_entity = kwargs[action.SOURCE_ENTITY]
        dungeon_level = source_entity.dungeon_level.value
        entities_in_sight = source_entity.vision.get_seen_entities()
        if not any(entities_in_sight):
            return
        entities_in_sight.append(source_entity)

        positions = [e.position.value for e in entities_in_sight]
        random.shuffle(positions)

        for entity in entities_in_sight:
            entity.mover.try_remove_from_dungeon()

        for entity in entities_in_sight:
            entity.mover.try_move(positions.pop(), dungeon_level)
        msg.send_global_message(messenger.SWAP_DEVICE_MESSAGE)


class HeartStopTriggeredEffect(TriggeredEffect):
    def __init__(self):
        super(HeartStopTriggeredEffect, self).__init__("heart_stop_triggered_effect")

    def trigger(self, **kwargs):
        source_entity = kwargs[action.SOURCE_ENTITY]
        ttl = gametime.single_turn * (random.randrange(3) + 2)
        entities = [entity for entity in source_entity.dungeon_level.value.entities
                    if entity.status_flags.has_status(StatusFlags.HAS_HEART) and not entity is source_entity]
        if len(entities) < 1:
            return
        target = random.sample(entities, 1)[0]
        heart_stop_effect = entityeffect.HeartStop(source_entity, time_to_live=ttl)
        target.effect_queue.add(heart_stop_effect)


class BlinksTriggeredEffect(TriggeredEffect):
    def __init__(self):
        super(BlinksTriggeredEffect, self).__init__("blinks_triggered_effect")

    def trigger(self, **kwargs):
        source_entity = kwargs[action.SOURCE_ENTITY]
        min_blinks = 2
        max_blinks = 6
        times = random.randrange(min_blinks, max_blinks + 1)
        for _ in range(times):
            self._blinks(source_entity)

    def _blinks(self, source_entity):
        player = source_entity
        entities = [entity for entity in source_entity.vision.get_seen_entities()] + [player]  # And the player too.
        for target_entity in entities:
            self._blink(target_entity)
        player.game_state.value.dungeon_needs_redraw = True
        player.game_state.value.force_draw()
        sleep(0.2)  # todo: standardise frame show time

    def _blink(self, entity):
        sight = entity.sight_radius.value
        possible_destinations = []
        for x in range(-sight, sight + 1):
            for y in range(-sight, sight + 1):
                if x == 0 and y == 0:
                    continue
                p = geometry.add_2d((x, y), entity.position.value)
                if entity.dungeon_mask.can_see_point(p):
                    possible_destinations.append(p)
        random.shuffle(possible_destinations)
        for position in possible_destinations:
            is_safe = (entity.dungeon_level.value.get_tile_or_unknown(position).get_terrain().has("is_floor")
                       or entity.status_flags.has_status(StatusFlags.FLYING))
            if is_safe and entity.mover.try_move(position):
                break


class HealAllSeenTriggeredEffect(TriggeredEffect):
    def __init__(self):
        super(HealAllSeenTriggeredEffect, self).__init__("heal_all_seen_triggered_effect")

    def trigger(self, **kwargs):
        source_entity = kwargs[action.SOURCE_ENTITY]
        player = source_entity
        entities = [entity for entity in source_entity.vision.get_seen_entities()
                    if entity.health.is_damaged()] + [player]  # And the player too.
        if len(entities) <= 0:
            return
        min_heal = 3
        max_heal = 15
        for target_entity in entities:
            heal = random.randrange(min_heal, max_heal + 1)
            heal_effect = entityeffect.Heal(target_entity, heal, heal_message=messenger.HEALTH_DEVICE_MESSAGE)
            target_entity.effect_queue.add(heal_effect)


class ZapRandomSeenEntityTriggeredEffect(TriggeredEffect):
    def __init__(self):
        super(ZapRandomSeenEntityTriggeredEffect, self).__init__("zap_random_seen_entity_triggered_effect")

    def trigger(self, **kwargs):
        source_entity = kwargs[action.SOURCE_ENTITY]
        entities = [entity for entity in source_entity.vision.get_seen_entities()
                    if not entity is source_entity]
        if len(entities) <= 0:
            return
        random.shuffle(entities)
        missile_hit_detector = MissileHitDetection(passes_entity=True, passes_solid=False)
        dungeon_level = source_entity.dungeon_level.value
        zap_graphic = GraphicChar(None, colors.LIGHT_ORANGE, "*")
        for entity in entities:
            path = util.get_path(source_entity.position.value, entity.position.value)
            path = path[1:]
            new_path = missile_hit_detector.get_path_taken(path, dungeon_level)
            if len(path) == len(new_path):
                self.zap_path(new_path, source_entity)
                animation.animate_path(source_entity.game_state.value, path, zap_graphic)
                break

    def zap_path(self, path, source_entity):
        for position in path:
            for entity in source_entity.dungeon_level.value.get_tile_or_unknown(position).get_entities():
                self.zap_entity(source_entity, entity)

    def zap_entity(self, source_entity, target_entity):
        damage_min = 1
        damage_max = 20
        damage_types = [DamageTypes.LIGHTNING]
        if target_entity.has("effect_queue"):
            damage = calculate_damage(damage_min, damage_max, 0, 1)
            damage_effect = entityeffect.UndodgeableAttackEntityEffect(source_entity, damage, damage_types,
                                                                       hit_message=messenger.ZAP_DEVICE_MESSAGE)
            target_entity.effect_queue.add(damage_effect)


class Stacker(Leaf):
    """
    Parent component is Stacker.

    Should only be used for items where all instances are equal.
    """

    def __init__(self, stack_type, max_size, size=1):
        super(Stacker, self).__init__()
        self.component_type = "stacker"
        self.stack_type = stack_type
        self.max_size = max_size
        self.size = size

    def is_full(self):
        return self.size >= self.max_size


class AddSpoofChildEquipEffect(Leaf):
    def __init__(self, spoof_child_factory, status_icon=None):
        super(AddSpoofChildEquipEffect, self).__init__()
        self.component_type = "equipment_add_spoof_component_" + spoof_child_factory().component_type
        self.tags.add("equipped_effect")

        self.spoof_child_factory = spoof_child_factory
        self.status_icon = status_icon

    def equipped_effect(self, entity):
        """
        Causes the entity that equips this have a spoofed component child.
        """
        entity.effect_queue.add(entityeffect.AddSpoofChild(entity, self.spoof_child_factory(), 1))
        if self.status_icon:
            entity.effect_queue.add(entityeffect.StatusIconEntityEffect(entity, self.status_icon, 1))


class AddSpoofChildEquipEffect2(Leaf):
    def __init__(self, spoof_child, status_icon=None):
        super(AddSpoofChildEquipEffect2, self).__init__()
        self.component_type = "equipment_add_spoof_component_" + spoof_child.component_type
        self.tags.add("equipped_effect")

        self.spoof_child = spoof_child
        self.status_icon = status_icon

    def equipped_effect(self, entity):
        """
        Causes the entity that equips this have a spoofed component child.
        """
        entity.effect_queue.add(entityeffect.AddSpoofChild(entity, self.spoof_child, 1))
        if self.status_icon:
            entity.effect_queue.add(entityeffect.StatusIconEntityEffect(entity, self.status_icon, 1))


class MoveTriggeredEffect(TriggeredEffect):
    def __init__(self):
        super(MoveTriggeredEffect, self).__init__("move_triggered_effect")

    def trigger(self, **kwargs):
        target_entity = kwargs[action.TARGET_ENTITY]
        source_entity = kwargs[action.SOURCE_ENTITY]
        target_position = kwargs[action.TARGET_POSITION]
        target_entity.mover.try_move(target_position, source_entity.dungeon_level.value)


class RemoveAChargeEffect(TriggeredEffect):
    def __init__(self):
        super(RemoveAChargeEffect, self).__init__("remove_a_charge_effect")

    def trigger(self, **kwargs):
        self.parent.item.value.charge.charges -= 1

    def can_trigger(self, **kwargs):
        return self.parent.item.value.charge.charges > 0


class HealTriggeredEffect(TriggeredEffect):
    def __init__(self, min_heal, max_heal, message=None):
        super(HealTriggeredEffect, self).__init__("heal_triggered_effect")
        self.max_heal = max_heal
        self.min_heal = min_heal
        self.message = message

    def trigger(self, **kwargs):
        target_entity = kwargs[action.TARGET_ENTITY]
        heal = random.randrange(self.min_heal, self.max_heal + 1)
        heal_effect = entityeffect.Heal(target_entity, heal, heal_message=self.message)
        target_entity.effect_queue.add(heal_effect)


class ApplyPoisonTriggeredEffect(TriggeredEffect):
    def __init__(self, min_damage, max_damage):
        super(ApplyPoisonTriggeredEffect, self).__init__("apply_poison_triggered_effect")
        self.max_damage = max_damage
        self.min_damage = min_damage

    def trigger(self, **kwargs):
        target_entity = kwargs[action.TARGET_ENTITY]
        damage = random.randrange(self.min_damage, self.max_damage + 1)
        damage_effect_factory = PoisonEntityEffectFactory(target_entity, damage, 2, random.randrange(8, 12))
        target_entity.effect_queue.add(damage_effect_factory())


class CreateFlameCloudTriggeredEffect(TriggeredEffect):
    def __init__(self):
        super(CreateFlameCloudTriggeredEffect, self).__init__("create_flame_cloud_triggered_effect")

    def trigger(self, **kwargs):
        min_fire_time = 3
        max_fire_time = 8
        game_state = kwargs[action.GAME_STATE]
        source_entity = kwargs[action.SOURCE_ENTITY]
        target_position = kwargs[action.TARGET_POSITION]
        put_tile_and_surrounding_tiles_on_fire(source_entity.dungeon_level.value, target_position, min_fire_time,
                                               max_fire_time, game_state)


class ExplodeTriggeredEffect(TriggeredEffect):
    def __init__(self):
        super(ExplodeTriggeredEffect, self).__init__("explode_triggered_effect")

    def trigger(self, **kwargs):
        #message = messenger.ENTITY_EXPLODES % {"target_entity": self.parent.description.name}
        source_entity = kwargs[action.SOURCE_ENTITY]
        target_position = kwargs[action.TARGET_POSITION]
        game_state = kwargs[action.GAME_STATE]
        explosion = new_explosion_cloud(game_state, 1)
        explosion.graphic_char.color_fg = colors.YELLOW
        explosion.mover.replace_move(target_position, source_entity.dungeon_level.value)
        for d in direction.DIRECTIONS:
            if d in direction.AXIS_DIRECTIONS:
                color = colors.ORANGE
            else:
                color = colors.RED
            point = geometry.add_2d(d, target_position)
            explosion = new_explosion_cloud(game_state, 1)
            explosion.graphic_char.color_fg = color
            explosion.mover.replace_move(point, source_entity.dungeon_level.value)

def put_tile_and_surrounding_tiles_on_fire(dungeon_level, position, min_fire_time, max_fire_time, game_state):
    fire = new_fire_cloud(game_state, random.randrange(min_fire_time, max_fire_time))
    fire.mover.replace_move(position, dungeon_level)
    for d in direction.DIRECTIONS:
        point = geometry.add_2d(d, position)
        fire = new_fire_cloud(game_state, random.randrange(min_fire_time, max_fire_time))
        fire.mover.replace_move(point, dungeon_level)


class CreateCloudTriggeredEffect(TriggeredEffect):
    def __init__(self, cloud_factory, density=32):
        super(CreateCloudTriggeredEffect, self).__init__("create_cloud_triggered_effect")
        self.density = density
        self.cloud_factory = cloud_factory

    def trigger(self, **kwargs):
        source_entity = kwargs[action.SOURCE_ENTITY]
        target_position = kwargs[action.TARGET_POSITION]
        game_state = kwargs[action.GAME_STATE]
        steam = self.cloud_factory(game_state, self.density)
        steam.mover.try_move(target_position, source_entity.dungeon_level.value)


class ApplyFrostTriggeredEffect(TriggeredEffect):
    def __init__(self):
        super(ApplyFrostTriggeredEffect, self).__init__("apply_frost_triggered_action")

    def trigger(self, **kwargs):
        target_entity = kwargs[action.TARGET_ENTITY]
        slow_turns = random.randrange(10, 19)
        msg.send_global_message(messenger.FROST_POTION_DRINK_MESSAGE)
        target_entity.effect_queue.add(entityeffect.AddSpoofChild(None, frost_effect_factory(),
                                                                  slow_turns * gametime.single_turn, meld_id="frost",
                                                                  status_description=FROST_SLOW_STATUS_DESCRIPTION))


class ReEquipAction(Action):
    """
    An Item with this component can be equipped on an entity.

    If an item is already in that
    equipment slot that item will be unequipped first.
    """

    def __init__(self):
        super(ReEquipAction, self).__init__()
        self.component_type = "reequip_action"
        self.tags.add("reequip_action")
        self.name = "Equip"
        self.display_order = 90

    def act(self, **kwargs):
        """
        Will attempt to equip the parent item to the given entity.
        """
        source_entity = kwargs[action.SOURCE_ENTITY]
        if action.EQUIPMENT_SLOT in kwargs:
            equipment_slot = kwargs[action.EQUIPMENT_SLOT]
        else:
            equipment_slot = self.get_equipment_slot(source_entity)
        old_item = None
        if source_entity.equipment.slot_is_equiped(equipment_slot):
            old_item = source_entity.equipment.unequip(equipment_slot)
        self._re_equip(source_entity, equipment_slot)
        if not old_item is None:
            source_entity.inventory.try_add(old_item)
        self.add_energy_spent_to_entity(source_entity)

    def get_equipment_slot(self, source_entity):
        """
        Finds the right equipment slot.
        """
        open_slots = (source_entity.equipment.get_open_slots_of_type
                      (self.parent.equipment_type.value))
        if len(open_slots) > 0:
            return open_slots[0]
        else:
            return (source_entity.equipment.get_slots_of_type
                    (self.parent.equipment_type.value))[0]

    def can_act(self, **kwargs):
        """
        Returns true if it is a valid action to reequip that item.
        """
        return True

    def _re_equip(self, target_entity, equipment_slot):
        """
        Performs the actual reequip.
        """
        re_equip_effect = entityeffect.ReEquip(target_entity, equipment_slot, self.parent)
        target_entity.effect_queue.add(re_equip_effect)
        target_entity.inventory.remove_item(self.parent)


class DropItemTriggeredEffect(TriggeredEffect):
    def __init__(self):
        super(DropItemTriggeredEffect, self).__init__("drop_item_triggered_effect")

    def trigger(self, **kwargs):
        """
        Attempts to drop the parent item at the entity's feet.
        """
        source_entity = kwargs[action.SOURCE_ENTITY]
        item = self.get_relative_of_type("item").value
        if not source_entity.inventory is None:
            if source_entity.inventory.try_drop_item(item):
                util.add_energy_spent_to_entity(source_entity, gametime.single_turn)
        return


class AddEnergySpentEffect(TriggeredEffect):
    def __init__(self, energy_cost=gametime.single_turn):
        super(AddEnergySpentEffect, self).__init__("add_energy_spent_effect")
        self.energy_cost = energy_cost

    def trigger(self, **kwargs):
        source_entity = kwargs[action.SOURCE_ENTITY]
        source_entity.actor.newly_spent_energy += self.energy_cost


class PutToSleepTriggeredEffect(TriggeredEffect):
    def __init__(self):
        super(PutToSleepTriggeredEffect, self).__init__("put_to_sleep_effect")

    def trigger(self, **kwargs):
        """
        When an entity reads a scroll of sleep it will put enemies in sight to sleep.
        """
        target_entity = kwargs[action.TARGET_ENTITY]
        entities_in_sight = target_entity.vision.get_seen_entities_closest_first()
        for entity in entities_in_sight:
            entity.set_child(TryPutToSleep())


class RemoveItemEffect(TriggeredEffect):
    def __init__(self):
        super(RemoveItemEffect, self).__init__("remove_item_effect")

    def trigger(self, **kwargs):
        target_entity = kwargs[action.SOURCE_ENTITY]
        item = self.get_relative_of_type("item").value
        target_entity.inventory.remove_one_item_from_stack(item)


class FlashItemEffect(TriggeredEffect):
    def __init__(self):
        super(FlashItemEffect, self).__init__("flash_item_effect")

    def trigger(self, **kwargs):
        source_entity = kwargs[action.SOURCE_ENTITY]
        item = self.get_relative_of_type("item").value
        _item_flash_animation(source_entity, item)


class LocalMessageEffect(TriggeredEffect):
    def __init__(self, message):
        super(LocalMessageEffect, self).__init__("local_message_effect")
        self.message = message

    def trigger(self, **kwargs):
        source_entity = kwargs[action.SOURCE_ENTITY]
        target_entity = kwargs[action.TARGET_ENTITY]
        message_arguments = {}
        if source_entity and source_entity.has("description"):
            message_arguments["source_entity"] = source_entity.description.long_name
        if target_entity and target_entity.has("description"):
            message_arguments["target_entity"] = target_entity.description.long_name

        msg.send_visual_message(self.message % message_arguments, source_entity.position.value)


class TeleportTriggeredEffect(TriggeredEffect):
    def __init__(self):
        super(TeleportTriggeredEffect, self).__init__("teleport_triggered_effect")

    def trigger(self, **kwargs):
        """
        teleports target entity.
        """
        target_entity = kwargs[action.TARGET_ENTITY]
        msg.send_global_message(messenger.PLAYER_TELEPORT_MESSAGE)
        teleport_effect = entityeffect.Teleport(target_entity)
        target_entity.effect_queue.add(teleport_effect)


class SingleSwapTriggeredEffect(TriggeredEffect):
    def __init__(self):
        super(SingleSwapTriggeredEffect, self).__init__("single_swap_triggered_effect")

    def trigger(self, **kwargs):
        """
        swaps target entity with another random entity on the floor.
        """
        source_entity = kwargs[action.SOURCE_ENTITY]
        dungeon_level = source_entity.dungeon_level.value
        other_entities = [e for e in dungeon_level.entities if not e is source_entity]
        if not any(other_entities):
            return

        random.shuffle(other_entities)

        other_entity = other_entities[0]
        other_pos = other_entity.position.value
        my_pos = source_entity.position.value

        other_entity.mover.try_remove_from_dungeon()
        source_entity.mover.try_remove_from_dungeon()

        source_entity.mover.try_move(other_pos, dungeon_level)
        other_entity.mover.try_move(my_pos, dungeon_level)
        source_entity.game_state.value.dungeon_needs_redraw = True
        msg.send_global_message(messenger.PLAYER_SWITCH_MESSAGE)


class MagicMappingTriggeredEffect(TriggeredEffect):
    def __init__(self, energy_cost=gametime.single_turn):
        super(MagicMappingTriggeredEffect, self).__init__("drop_item_triggered_effect")
        self.energy_cost = energy_cost

    def trigger(self, **kwargs):
        """
        Attempts to drop the parent item at the entity's feet.
        """
        target_entity = kwargs[action.TARGET_ENTITY]
        msg.send_global_message(messenger.PLAYER_MAP_MESSAGE)
        dungeon_level = target_entity.dungeon_level.value
        walkable_positions = dungeon_level.get_walkable_positions(dummy_flyer_open_doors, target_entity.position.value)
        map_positions = extend_points(walkable_positions)
        for p in map_positions:
            tile = dungeon_level.get_tile_or_unknown(p)
            target_entity.memory_map.gain_knowledge_of_terrain_of_tile(tile, p, dungeon_level.depth)
        target_entity.game_state.value.dungeon_needs_redraw = True


class PushOthersTriggeredEffect(TriggeredEffect):
    def __init__(self):
        super(PushOthersTriggeredEffect, self).__init__("push_others_triggered_effect")

    def trigger(self, **kwargs):
        """
        Attempts to drop the parent item at the entity's feet.
        """
        target_entity = kwargs[action.TARGET_ENTITY]
        entities_in_sight = target_entity.vision.get_seen_entities_closest_first()
        entities_in_sight.reverse()
        if not any(entities_in_sight):
            return
        min_push = 2
        max_push = 4
        entity_direction = {}
        entity_push_steps = {}
        max_push_distance = 0
        for entity in entities_in_sight:
            push_direction = geometry.other_side_of_point_direction(target_entity.position.value, entity.position.value)
            entity_direction[entity] = push_direction
            entity_push_steps[entity] = random.randrange(min_push, max_push + 1)
            max_push_distance = max(entity_push_steps[entity], max_push_distance)
        for index in range(max_push_distance):
            for entity in entities_in_sight:
                if (entity_push_steps[entity] <= index or
                        self._entity_is_about_to_fall(entity)):
                    break
                entity.stepper.try_push_in_direction(entity_direction[entity])
            target_entity.game_state.value.dungeon_needs_redraw = True
            target_entity.game_state.value.force_draw()
            sleep(0.07)  # todo: standardise frame show time
        msg.send_global_message(messenger.PLAYER_PUSH_SCROLL_MESSAGE)

    def _entity_is_about_to_fall(self, entity):
        if entity.status_flags.has_status(StatusFlags.FLYING):
            return False
        dungeon_level = entity.dungeon_level.value
        tile = dungeon_level.get_tile_or_unknown(entity.position.value)
        result = tile.get_terrain().has("is_chasm")
        return result


class PickUpItemAction(Action):
    """
    An entity will be able to pick up items.
    """

    def __init__(self):
        super(PickUpItemAction, self).__init__()
        self.component_type = "pick_up_item_action"
        self.name = "Pick Up"
        self.display_order = 70

    def can_act(self, **kwargs):
        """
        Returns true if it's possible for the
        source_entity to pickup the parent item.
        """
        source_entity = kwargs[action.SOURCE_ENTITY]
        item = self._get_item_on_floor(source_entity)
        return (not item is None and
                source_entity.inventory.has_room_for_item(item))

    def act(self, **kwargs):
        """
        Performs the pickup action.
        """
        source_entity = kwargs[action.SOURCE_ENTITY]
        item = self._get_item_on_floor(source_entity)
        if item is None:
            raise Exception("Could not find item on floor.", source_entity, item)
        pickup_succeded = self.parent.inventory.try_add(item)
        if pickup_succeded:
            item.remove_component_of_type("player_auto_pick_up")
            msg.send_visual_message(messenger.PICK_UP_MESSAGE % {"item": item.description.name},
                                    source_entity.position.value)
            self.parent.actor.newly_spent_energy += gametime.single_turn
            _item_flash_animation(source_entity, item)

    def _get_item_on_floor(self, entity):
        dungeon_level = entity.dungeon_level.value
        position = entity.position.value
        return dungeon_level.get_tile(position).get_first_item()

    def print_player_error(self, **kwargs):
        """
        Prints a message to the user explaining what went wrong.
        """
        source_entity = kwargs[action.SOURCE_ENTITY]
        item = self._get_item_on_floor(source_entity)
        if (not item is None and
                not self.parent.inventory.has_room_for_item(item)):
            message = "Could not pick up: " + item.description.name + \
                      ", the inventory is full."
            msg.send_visual_message(message, source_entity.position.value)


class EquipmentType(Leaf):
    """
    Holds the equipment type of a equipment item.
    """

    def __init__(self, equipment_type):
        super(EquipmentType, self).__init__()
        self.component_type = "equipment_type"
        self.value = equipment_type


class OnUnequipEffect(Leaf):
    """
    Parent items with this component has a effect that happens on equipping.
    """

    def __init__(self, effect_function):
        super(OnUnequipEffect, self).__init__()
        self.component_type = "on_unequip_effect"
        self.effect = effect_function


class PlayerAutoPickUp(Leaf):
    """
    Items with this component, should trigger the player auto pick up of the item.
    """

    def __init__(self):
        super(PlayerAutoPickUp, self).__init__()
        self.component_type = "player_auto_pick_up"


class OnEquipEffect(Leaf):
    """
    Parent items with this component has a effect that happens on equipping.
    """

    def __init__(self, effect_function):
        super(OnEquipEffect, self).__init__()
        self.component_type = "on_equip_effect"
        self.effect = effect_function


class ItemType(Leaf):
    """
    Enumerator class denoting different item types. Inventory is sorted on ItemType.
    """
    POTION = 0
    SCROLL = 1
    BOMB = 2
    DEVICE = 3
    WEAPON = 4
    ARMOR = 5
    JEWELLRY = 6
    AMMO = 7
    ENERGY_SHPERE = 7

    ALL = [POTION, BOMB, DEVICE, WEAPON, ARMOR, JEWELLRY, AMMO, ENERGY_SHPERE]

    def __init__(self, item_type):
        super(ItemType, self).__init__()
        self.component_type = "item_type"
        self.value = item_type


def _item_flash_animation(entity, item):
    entity.char_printer.append_graphic_char_temporary_frames([item.graphic_char])