import random

from action import Action
from cloud import new_steam_cloud, new_explosion_cloud
from compositecore import Leaf, Composite
from attacker import Attack, DamageTypes
import direction
import geometry
from graphic import GraphicChar, CharPrinter
import messenger
from missileaction import PlayerThrowItemAction
from mover import Mover
from position import Position, DungeonLevel
import rng
from stats import DataPointBonusSpoof, DataPoint, Flag, DataTypes, GamePieceTypes
from statusflags import StatusFlags
from text import Description
import action
import colors
import entityeffect
import equipment
import gametime
from messenger import msg
import icon


class ItemType(Leaf):
    """
    Enumerator class denoting different item types. Inventory is sorted on ItemType.
    """
    POTION = 0
    BOMB = 1
    MACHINE = 2
    WEAPON = 3
    ARMOR = 4
    JEWELLRY = 5
    AMMO = 6

    ALL = [POTION, BOMB, MACHINE, WEAPON, ARMOR, JEWELLRY, AMMO]

    def __init__(self, item_type):
        super(ItemType, self).__init__()
        self.component_type = "item_type"
        self.value = item_type


def set_item_components(item):
    item.set_child(Position())
    item.set_child(DungeonLevel())
    item.set_child(Mover())
    item.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.ITEM))
    item.set_child(CharPrinter())
    item.set_child(DropAction())
    item.set_child(PlayerThrowItemAction())
    item.set_child(ThrowerNonBreak())
    return item


def set_ranged_weapon_components(item):
    item.set_child(EquipmentType(equipment.EquipmentTypes.RANGED_WEAPON))
    item.set_child(ItemType(ItemType.WEAPON))
    item.set_child(ReEquipAction())


def new_gun():
    gun = Composite()
    set_item_components(gun)
    set_ranged_weapon_components(gun)
    gun.set_child(RangeWeaponType(RangeWeaponType.GUN))
    gun.set_child(Description("Gun",
                              "This was once a fine weapon, \
                               but age has torn it real bad.\n\
                               The wooden handle is dry and gray, \
                               you see rust eating into the iron pipe."))
    gun.set_child(GraphicChar(None, colors.WHITE, icon.GUN))
    gun.set_child(DamageProvider(15, 10, [DamageTypes.PHYSICAL,
                                          DamageTypes.PIERCING]))
    gun.set_child(DataPoint(DataTypes.WEAPON_RANGE, 15))
    gun.set_child(DataPoint(DataTypes.HIT, 13))
    gun.set_child(DataPoint(DataTypes.WEIGHT, 5))
    return gun


def new_sling():
    sling = Composite()
    set_item_components(sling)
    set_ranged_weapon_components(sling)
    sling.set_child(RangeWeaponType(RangeWeaponType.SLING))
    sling.set_child(Description("Sling",
                                "This weapon propels rocks more effectively than throwing them would."))
    sling.set_child(GraphicChar(None, colors.ORANGE, icon.SLING))
    sling.set_child(DataPoint(DataTypes.WEAPON_RANGE, 4))
    sling.set_child(DamageProvider(1, 2, [DamageTypes.PHYSICAL, DamageTypes.PIERCING]))
    sling.set_child(DataPoint(DataTypes.WEIGHT, 3))
    sling.set_child(DataPoint(DataTypes.HIT, 5))
    return sling


class RangeWeaponType(DataPoint):
    """
    Component that marks a weapon as a ranged weapon.
    """

    GUN = 0
    SLING = 1

    def __init__(self, range_weapon_type):
        super(RangeWeaponType, self).__init__("range_weapon_type", range_weapon_type)


def set_device_components(item):
    item.set_child(ItemType(ItemType.MACHINE))
    item.set_child(PlayerAutoPickUp())
    item.set_child(Charge(random.randrange(2, 7)))
    item.set_child(DataPoint(DataTypes.WEIGHT, 5))
    return item


class Charge(Leaf):
    def __init__(self, charges):
        super(Charge, self).__init__()
        self.component_type = "charge"
        self.charges = charges


def new_darkness_device():
    device = Composite()
    set_item_components(device)
    set_device_components(device)
    device.set_child(Description("Device of Darkness",
                                 "This ancient device will dim the vision of all creatures on the floor."))
    device.set_child(DarknessDeviceAction())
    device.set_child(GraphicChar(None, colors.GREEN, icon.MACHINE))
    return device


def new_heart_stop_device():
    device = Composite()
    set_item_components(device)
    set_device_components(device)
    device.set_child(Description("Dev. of Heart Stop",
                                 "This ancient device will cause a random creature on the floor to have a heart attack."))
    device.set_child(HeartStopDeviceAction())
    device.set_child(GraphicChar(None, colors.BLUE, icon.MACHINE))
    return device


class ActivateDeviceAction(Action):
    def __init__(self):
        super(ActivateDeviceAction, self).__init__()
        self.name = "Activate"
        self.display_order = 90

    def act(self, **kwargs):
        """
        Performs the drink action, subclasses should not override this.
        """
        source_entity = kwargs[action.SOURCE_ENTITY]

        self._activate(source_entity)
        _item_flash_animation(source_entity, self.parent)
        self.parent.charge.charges -= 1
        self.add_energy_spent_to_entity(source_entity)

    def can_act(self, **kwargs):
        """
        You cannot use a device without charges.
        """
        return self.parent.charge.charges > 0

    def _activate(self, source_entity):
        """
        The activate action subclasses should override
        and define the activate action here.
        """
        pass


class DarknessDeviceAction(ActivateDeviceAction):
    """
    Defines the device activate action.
    """

    def __init__(self):
        super(DarknessDeviceAction, self).__init__()
        self.component_type = "darkness_device_activate_action"

    def _activate(self, source_entity):
        """
        The activate action subclasses should override
        and define the activate action here.
        """
        ttl = gametime.single_turn * rng.random_variance(10, 5)
        entities = source_entity.dungeon_level.value.entities
        for entity in entities:
            sight_radius_spoof = DataPoint(DataTypes.SIGHT_RADIUS, 1)
            darkness_effect = entityeffect.AddSpoofChild(source_entity, sight_radius_spoof, time_to_live=ttl)
            entity.effect_queue.add(darkness_effect)
            msg.send_global_message(messenger.DARKNESS_MESSAGE)


class HeartStopDeviceAction(ActivateDeviceAction):
    """
    Defines the device activate action.
    """

    def __init__(self):
        super(HeartStopDeviceAction, self).__init__()
        self.component_type = "heart_stop_device_activate_action"

    def _activate(self, source_entity):
        """
        The activate action subclasses should override
        and define the activate action here.
        """
        ttl = gametime.single_turn * (random.randrange(3) + 2)
        entities = [entity for entity in source_entity.dungeon_level.value.entities
                    if entity.status_flags.has_status(StatusFlags.HAS_HEART) and not entity is source_entity]
        if len(entities) < 1:
            return
        target = random.sample(entities, 1)[0]
        heart_stop_effect = entityeffect.HeartStop(source_entity, time_to_live=ttl)
        target.effect_queue.add(heart_stop_effect)


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


def new_ammunition():
    """
    A composite component representing a gun ammunition item.
    """
    ammo = Composite()
    set_item_components(ammo)
    ammo.set_child(ItemType(ItemType.AMMO))
    ammo.set_child(Flag("is_ammo"))
    ammo.set_child(Stacker("ammo", 10, random.randrange(2, 6)))
    ammo.set_child(Description("Gun Bullets",
                               "These bullets will fit in most guns."))
    ammo.set_child(GraphicChar(None, colors.GRAY, icon.AMMO2))
    ammo.set_child(DataPoint(DataTypes.WEIGHT, 1))
    ammo.set_child(PlayerAutoPickUp())
    return ammo


class EquippedEffect(Leaf):
    """
    Parent items with this component has a
    effect that happens while item is equipped.
    """

    def __init__(self):
        super(EquippedEffect, self).__init__()
        self.component_type = "equipped_effect"

    def effect(self, entity):
        pass


def set_armor_components(item):
    item.set_child(ItemType(ItemType.ARMOR))
    item.set_child(ReEquipAction())
    return item


def new_leather_armor():
    """
    A composite component representing a Armor item.
    """
    armor = Composite()
    set_item_components(armor)
    set_armor_components(armor)
    armor.set_child(Description("Leather Armor",
                                "A worn leather armor. It's old, but should still protect you from some damage."))
    armor.set_child(GraphicChar(None, colors.ORANGE_D, icon.ARMOR))
    armor.set_child(StatBonusEquipEffect("armor", 2))
    armor.set_child(EquipmentType(equipment.EquipmentTypes.ARMOR))
    armor.set_child(DataPoint(DataTypes.WEIGHT, 10))
    return armor


def new_leather_boots():
    """
    A composite component representing a Boots Armor item.
    """
    boots = Composite()
    set_item_components(boots)
    set_armor_components(boots)
    boots.set_child(Description("Leather Boots",
                                "A worn pair of boots, dry mud covers most of the leather."))
    boots.set_child(DataPoint(DataTypes.WEIGHT, 4))
    boots.set_child(GraphicChar(None, colors.ORANGE_D, icon.BOOTS))
    boots.set_child(StatBonusEquipEffect("armor", 1))
    boots.set_child(EquipmentType(equipment.EquipmentTypes.BOOTS))
    return boots


def new_leather_cap():
    """
    A composite component representing a Armor item.
    """
    cap = Composite()
    set_item_components(cap)
    set_armor_components(cap)
    cap.set_child(Description("Leather Cap",
                              "An old cap made out of leather, this should keep some harm away."))
    cap.set_child(DataPoint(DataTypes.WEIGHT, 4))
    cap.set_child(GraphicChar(None, colors.ORANGE_D, icon.HELM))
    cap.set_child(StatBonusEquipEffect("armor", 1))
    cap.set_child(EquipmentType(equipment.EquipmentTypes.HEADGEAR))
    return cap


def set_melee_weapon_component(item):
    item.set_child(EquipmentType(equipment.EquipmentTypes.MELEE_WEAPON))
    item.set_child(ItemType(ItemType.WEAPON))
    item.set_child(ReEquipAction())


def new_sword():
    """
    A composite component representing a Sword item.
    """
    sword = Composite()
    set_item_components(sword)
    set_melee_weapon_component(sword)
    sword.set_child(Description("Iron Sword",
                                "This old blade has seen some better days, it's as sharp as ever tough."))
    sword.set_child(GraphicChar(None, colors.GRAY, icon.SWORD))
    sword.set_child(DamageProvider(4, 1, [DamageTypes.PHYSICAL, DamageTypes.CUTTING]))
    sword.set_child(DataPoint(DataTypes.WEIGHT, 10))
    sword.set_child(DataPoint(DataTypes.HIT, 16))
    return sword


def new_knife():
    """
    A composite component representing a Knife item.
    """
    knife = Composite()
    set_item_components(knife)
    set_melee_weapon_component(knife)
    knife.set_child(Description("Knife", "A trusty knife, small and precise but will only inflict small wounds."))
    knife.set_child(GraphicChar(None, colors.GRAY, icon.KNIFE))
    knife.set_child(DamageProvider(2, 1, [DamageTypes.PHYSICAL, DamageTypes.CUTTING]))
    knife.set_child(DataPoint(DataTypes.WEIGHT, 5))
    knife.set_child(DataPoint(DataTypes.HIT, 21))
    return knife


def set_ring_components(item):
    item.set_child(EquipmentType(equipment.EquipmentTypes.RING))
    item.set_child(ItemType(ItemType.JEWELLRY))
    item.set_child(ReEquipAction())
    item.set_child(DataPoint(DataTypes.WEIGHT, 2))


def new_ring_of_invisibility():
    ring = Composite()
    set_item_components(ring)
    set_ring_components(ring)
    ring.set_child(GraphicChar(None, colors.CYAN, icon.RING))
    ring.set_child(SetInvisibilityFlagEquippedEffect())
    ring.set_child(Description("Ring of Invisibility",
                               "The metal is warm to your skin, "
                               "this ring will make you invisible"))
    return ring


def new_ring_of_evasion():
    ring = Composite()
    set_item_components(ring)
    set_ring_components(ring)
    ring.set_child(GraphicChar(None, colors.GREEN, icon.RING))
    ring.set_child(StatBonusEquipEffect("evasion", 3))
    ring.set_child(Description("Ring of Evasion",
                               "The ring is light on your finger, "
                               "Its magic powers makes it easier for you to dodge attacks."))
    return ring


def new_ring_of_stealth():
    ring = Composite()
    set_item_components(ring)
    set_ring_components(ring)
    ring.set_child(GraphicChar(None, colors.BLUE, icon.RING))
    ring.set_child(StatBonusEquipEffect("stealth", 3))
    ring.set_child(Description("Ring of Stealth",
                               "The ring is smooth to your skin, "
                               "Its magic powers makes it easier for you to sneak past enemies."))
    return ring


def new_ring_of_strength():
    ring = Composite()
    set_item_components(ring)
    set_ring_components(ring)
    ring.set_child(GraphicChar(None, colors.ORANGE, icon.RING))
    ring.set_child(StatBonusEquipEffect("strength", 3))
    ring.set_child(Description("Ring of Strength",
                               "The ring feels unnaturally heavy, "
                               "Its magic powers makes you stronger."))
    return ring


class StatBonusEquipEffect(EquippedEffect):
    def __init__(self, stat, bonus):
        super(StatBonusEquipEffect, self).__init__()
        self.stat = stat
        self.bonus = bonus

    def effect(self, entity):
        """
        Causes the entity that equips this have a bonus to one stat.
        """
        entity.add_spoof_child(DataPointBonusSpoof(self.stat, self.bonus))


class SetInvisibilityFlagEquippedEffect(EquippedEffect):
    def __init__(self):
        super(SetInvisibilityFlagEquippedEffect, self).__init__()

    def effect(self, entity):
        """
        Causes the entity that equips this item to become invisible.
        """
        invisible_flag = entity.StatusFlags.INVISIBILE
        invisibility_effect = entityeffect.StatusAdder(self.parent, self.parent,
                                                       invisible_flag, time_to_live=1)
        self.parent.effect_queue.add(invisibility_effect)


def set_potion_components(item):
    item.set_child(ItemType(ItemType.POTION))
    item.set_child(PlayerAutoPickUp())
    item.set_child(ThrowerCreateSteam())
    item.set_child(DataPoint(DataTypes.WEIGHT, 4))
    #potion.set_child(Stacker("health_potion", 3))


def new_health_potion():
    potion = Composite()
    set_item_components(potion)
    set_potion_components(potion)
    potion.set_child(GraphicChar(None, colors.PINK, icon.POTION))
    potion.set_child(HealthPotionDrinkAction())
    potion.set_child(Description("Health Potion",
                                 "An unusually thick liquid contained in a glass bottle."
                                 "Drinking from it will heal you."))
    return potion


def new_bomb():
    bomb = Composite()
    set_item_components(bomb)
    bomb.set_child(ItemType(ItemType.BOMB))
    bomb.set_child(PlayerAutoPickUp())
    bomb.set_child(GraphicChar(None, colors.DARK_GRAY, icon.BOMB))
    bomb.set_child(DataPoint(DataTypes.WEIGHT, 4))
    bomb.set_child(Description("Bomb",
                               "A ball filled gunpowder, with a fuse attached."
                               "Throwing it will cause some serious damage."))
    bomb.set_child(ThrowerCreateExplosion())
    return bomb


class DropAction(Action):
    """
    An entity holding the parent item in its inventory should be able to drop
    the item using this action.
    """

    def __init__(self):
        super(DropAction, self).__init__()
        self.component_type = "drop_action"
        self.name = "Drop"
        self.display_order = 110

    def act(self, **kwargs):
        """
        Attempts to drop the parent item at the entity's feet.
        """
        source_entity = kwargs[action.SOURCE_ENTITY]
        if not source_entity.inventory is None:
            drop_successful = \
                source_entity.inventory.try_drop_item(self.parent)
            if drop_successful:
                self.add_energy_spent_to_entity(source_entity)
        return


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
        re_equip_effect = \
            entityeffect.ReEquip(target_entity, equipment_slot, self.parent)
        target_entity.effect_queue.add(re_equip_effect)
        target_entity.inventory.remove_item(self.parent)


class DrinkAction(Action):
    """
    Abstract class, drink actions should inherit from this class.
    """

    def __init__(self):
        super(DrinkAction, self).__init__()
        self.name = "Drink"
        self.tags.add("drink_action")
        self.display_order = 90

    def act(self, **kwargs):
        """
        Performs the drink action, subclasses should not override this.
        """
        target_entity = kwargs[action.TARGET_ENTITY]
        source_entity = kwargs[action.SOURCE_ENTITY]
        self._drink(target_entity)
        self.remove_from_inventory(target_entity)
        _item_flash_animation(source_entity, self.parent)
        self.add_energy_spent_to_entity(source_entity)

    def remove_from_inventory(self, target_entity):
        """
        Removes the parent item from the inventory.
        """
        target_entity.inventory.remove_one_item_from_stack(self.parent)

    def _drink(self, target_entity):
        """
        The drink action subclasses should override
        and define the drink action here.
        """
        pass


class HealthPotionDrinkAction(DrinkAction):
    """
    Defines the healing potion drink action.
    """

    def __init__(self):
        super(HealthPotionDrinkAction, self).__init__()
        self.component_type = "health_potion_drink_action"
        self.min_heal = 10
        self.max_heal = 15

    def _drink(self, target_entity):
        """
        When an entity drinks a healing potion, it is healed.
        """
        heal = random.randrange(self.min_heal, self.max_heal + 1)
        heal_effect = entityeffect.Heal(target_entity, heal, heal_message=messenger.HEALTH_POTION_MESSAGE)
        target_entity.effect_queue.add(heal_effect)


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


class DamageProvider(Leaf):
    """
    The provides holds damage, actual damage will be calculated on use.
    """

    def __init__(self, damage, variance, types):
        super(DamageProvider, self).__init__()
        self.component_type = "damage_provider"
        self.damage = damage
        self.variance = variance
        self.types = types

    def damage_entity(self, source_entity, target_entity, bonus_damage=0, bonus_hit=0):
        damage_strength = self.damage + source_entity.strength.value / 2
        damage = Attack(damage_strength, self.variance,
                        self.types, self.parent.hit.value)
        return damage.damage_entity(source_entity, target_entity,
                                    bonus_damage=bonus_damage, bonus_hit=bonus_hit)


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


class Thrower(Leaf):
    """
    Items with this component can be thrown.
    """

    def __init__(self):
        super(Thrower, self).__init__()
        self.component_type = "thrower"

    def hit_ground_effect(self, position):
        """
        The effect of the item has when it hits the ground.

        position: The point at which the item hits the ground.
        """
        pass


class ThrowerNonBreak(Thrower):
    """
    Items with this component can be thrown, but will survive the fall.
    """

    def __init__(self):
        super(ThrowerNonBreak, self).__init__()

    def throw_effect(self, dungeon_level, position):
        """
        The item will be placed at the tile where it lands.

        position: The point at which the item hits the ground.
        """
        self.parent.mover.try_move(position, dungeon_level)
        message = "The " + self.parent.description.name.lower() + \
                  " hits the ground with a thud."
        msg.send_visual_message(message, position)


class ThrowerBreak(Thrower):
    """
    Items with this component can be thrown, but will survive the fall.
    """

    def __init__(self):
        super(ThrowerBreak, self).__init__()

    def throw_effect(self, dungeon_level, position):
        message = "The " + self.parent.description.name.lower() + \
                  " smashes to the ground and breaks into pieces."
        msg.send_visual_message(message, position)


class ThrowerCreateSteam(Thrower):
    """
    Items with this component will create and create a puff of steam.
    """

    def __init__(self):
        super(ThrowerCreateSteam, self).__init__()

    def throw_effect(self, dungeon_level, position):
        message = "The " + self.parent.description.name.lower() + \
                  " smashes to the ground and breaks into pieces."
        msg.send_visual_message(message, position)
        steam = new_steam_cloud(32)
        steam.mover.try_move(position, dungeon_level)


class ThrowerCreateExplosion(Thrower):
    """
    Items with this component will create and create a puff of steam.
    """

    def __init__(self):
        super(ThrowerCreateExplosion, self).__init__()

    def throw_effect(self, dungeon_level, position):
        message = "The " + self.parent.description.name.lower() + " Explodes!."
        msg.send_visual_message(message, position)
        explosion = new_explosion_cloud(1)
        explosion.graphic_char.color_fg = colors.RED
        explosion.mover.replace_move(position, dungeon_level)
        for d in direction.DIRECTIONS:
            if d in direction.AXIS_DIRECTIONS:
                color = colors.ORANGE
            else:
                color = colors.YELLOW
            point = geometry.add_2d(d, position)
            explosion = new_explosion_cloud(1)
            explosion.graphic_char.color_fg = color
            explosion.mover.replace_move(point, dungeon_level)


def _item_flash_animation(entity, item):
    entity.char_printer.append_graphic_char_temporary_frames([item.graphic_char])
