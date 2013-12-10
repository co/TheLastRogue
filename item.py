import random

from action import Action
from compositecore import Leaf, Composite
from attacker import Damage, DamageTypes
from graphic import GraphicChar, CharPrinter
from health import BlockDamageHealthSpoof
from missileaction import PlayerThrowItemAction
from mover import Mover
from position import Position, DungeonLevel
import rng
from stats import GamePieceType, Hit, DataPointBonusSpoof, DataPoint
from text import Description
import action
import colors
import entityeffect
import equipment
import gametime
from messenger import messenger
import icon
from vision import SightRadius


class ItemType(Leaf):
    """
    Enumerator class denoting different item types. Inventory is sorted on ItemType.
    """
    POTION = 0
    MACHINE = 1
    WEAPON = 2
    ARMOR = 3
    JEWELLRY = 4
    AMMO = 5

    ALL = [POTION, MACHINE, WEAPON, ARMOR, JEWELLRY, AMMO]

    def __init__(self, item_type):
        super(ItemType, self).__init__()
        self.component_type = "item_type"
        self.value = item_type


class Gun(Composite):
    """
    A composite component representing a Gun item.
    """

    def __init__(self):
        super(Gun, self).__init__()
        self.add_child(GamePieceType(GamePieceType.ITEM))
        self.add_child(EquipmentType(equipment.EquipmentTypes.RANGED_WEAPON))
        self.add_child(ItemType(ItemType.WEAPON))
        self.add_child(RangeWeaponType(RangeWeaponType.GUN))
        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(Mover())
        self.add_child(Description("Gun",
                                   "This was once a fine weapon, \
                                   but age has torn it real bad.\n\
                                   The wooden handle is dry and gray, \
                                   you see rust eating into the iron pipe."))
        self.add_child(GraphicChar(None, colors.WHITE, icon.GUN))
        self.add_child(CharPrinter())
        self.add_child(DamageProvider(15, 10, [DamageTypes.PHYSICAL,
                                               DamageTypes.PIERCING]))
        self.add_child(WeaponRange(15))
        self.add_child(ReEquipAction())
        self.add_child(DropAction())
        self.add_child(PlayerThrowItemAction())
        self.add_child(ThrowerNonBreak())
        self.add_child(Weight(5))
        self.add_child(Hit(13))


class Sling(Composite):
    """
    A composite component representing a Sling item.
    """
    def __init__(self):
        super(Sling, self).__init__()
        self.add_child(GamePieceType(GamePieceType.ITEM))
        self.add_child(EquipmentType(equipment.EquipmentTypes.RANGED_WEAPON))
        self.add_child(ItemType(ItemType.WEAPON))
        self.add_child(RangeWeaponType(RangeWeaponType.SLING))
        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(Mover())
        self.add_child(Description("Sling",
                                   "This weapon propels rocks more effectively than throwing them would."))
        self.add_child(GraphicChar(None, colors.ORANGE, icon.SLING))
        self.add_child(CharPrinter())
        self.add_child(WeaponRange(4))
        self.add_child(ReEquipAction())
        self.add_child(DropAction())
        self.add_child(PlayerThrowItemAction())
        self.add_child(ThrowerNonBreak())
        self.add_child(DamageProvider(1, 3, [DamageTypes.PHYSICAL,
                                             DamageTypes.PIERCING]))
        self.add_child(Weight(3))
        self.add_child(Hit(5))


class RangeWeaponType(DataPoint):
    """
    Component that marks a weapon as a ranged weapon.
    """

    GUN = 0
    SLING = 1

    def __init__(self, range_weapon_type):
        super(RangeWeaponType, self).__init__("range_weapon_type", range_weapon_type)


class Device(Composite):
    """
    A composite component representing a Gun item.
    """

    def __init__(self):
        super(Device, self).__init__()
        self.add_child(GamePieceType(GamePieceType.ITEM))
        self.add_child(ItemType(ItemType.MACHINE))
        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(Mover())
        self.add_child(Description("Ancient Device",
                                   "An ancient device, its creators are "
                                   "long dead. But what is it for?\n"))
        self.add_child(GraphicChar(None, colors.GREEN, icon.MACHINE))
        self.add_child(CharPrinter())
        self.add_child(DropAction())
        self.add_child(PlayerThrowItemAction())
        self.add_child(ThrowerNonBreak())
        self.add_child(Weight(5))
        self.add_child(Charge(random.randrange(2, 7)))


class Charge(Leaf):
    def __init__(self, charges):
        super(Charge, self).__init__()
        self.component_type = "charge"
        self.charges = charges


class DarknessDevice(Device):
    def __init__(self):
        super(DarknessDevice, self).__init__()
        self.description.name = "Device of Darkness"
        self.graphic_char.color_fg = colors.GREEN
        self.add_child(DarknessDeviceAction())


class HeartStopDevice(Device):
    def __init__(self):
        super(HeartStopDevice, self).__init__()
        self.description.name = "Dev. of Heart Stop"
        self.graphic_char.color_fg = colors.BLUE
        self.add_child(HeartStopDeviceAction())


class ActivateDeviceAction(Action):
    def __init__(self):
        super(ActivateDeviceAction, self).__init__()
        self.name = "Activate"
        self.display_order = 90

    def act(self, **kwargs):
        """
        Performs the drink action, subclasses should not override this.
        """
        target_entity = kwargs[action.TARGET_ENTITY]
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
            darkness_effect = entityeffect.AddSpoofChild(source_entity, SightRadius(1), time_to_live=ttl)
            entity.effect_queue.add(darkness_effect)


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
        entities = source_entity.dungeon_level.value.entities
        if source_entity in entities:
            entities.remove(source_entity)
        if len(entities) < 1:
            return
        target = random.sample(entities, 1)[0]
        heart_stop_effect = entityeffect.HeartStop(source_entity, time_to_live=ttl)
        target.effect_queue.add(heart_stop_effect)


class IsAmmo(Leaf):
    """
    Parent component holding this is some kind of ammo.
    """

    def __init__(self):
        super(IsAmmo, self).__init__()
        self.component_type = "is_ammo"


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


class Ammunition(Composite):
    """
    A composite component representing a gun ammunition item.
    """

    def __init__(self):
        super(Ammunition, self).__init__()
        self.add_child(GamePieceType(GamePieceType.ITEM))
        self.add_child(ItemType(ItemType.AMMO))
        self.add_child(Position())
        self.add_child(IsAmmo())
        self.add_child(Stacker("ammo", 10, 3))
        self.add_child(DungeonLevel())
        self.add_child(Mover())
        self.add_child(Description("Gun Bullets",
                                   "These bullets will fit in most guns."))
        self.add_child(GraphicChar(None, colors.GRAY, icon.AMMO2))
        self.add_child(DropAction())
        self.add_child(CharPrinter())
        self.add_child(Weight(1))


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


class Armor(Composite):
    """
    A composite component representing a Armor item.
    """

    def __init__(self):
        super(Armor, self).__init__()
        self.add_child(GamePieceType(GamePieceType.ITEM))
        self.add_child(ItemType(ItemType.ARMOR))
        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(Mover())
        self.add_child(CharPrinter())
        self.add_child(ReEquipAction())
        self.add_child(DropAction())
        self.add_child(PlayerThrowItemAction())
        self.add_child(ThrowerNonBreak())
        self.add_child(Weight(10))


class LeatherArmor(Armor):
    """
    A composite component representing a Armor item.
    """

    def __init__(self):
        super(LeatherArmor, self).__init__()
        self.add_child(Description("Leather Armor",
                                   "A worn leather armor. It's old, but should still protect you from some damage."))
        self.add_child(Weight(10))
        self.add_child(GraphicChar(None, colors.ORANGE_D, icon.ARMOR))
        self.add_child(BlockDamageEquippedEffect(1, 2, [DamageTypes.PHYSICAL]))
        self.add_child(EquipmentType(equipment.EquipmentTypes.ARMOR))


class LeatherBoots(Armor):
    """
    A composite component representing a Armor item.
    """

    def __init__(self):
        super(LeatherBoots, self).__init__()
        self.add_child(Description("Leather Boots",
                                   "A worn pair of boots, dry mud covers most of the leather."))
        self.add_child(Weight(4))
        self.add_child(GraphicChar(None, colors.ORANGE_D, icon.BOOTS))
        self.add_child(BlockDamageEquippedEffect(0, 1, [DamageTypes.PHYSICAL]))
        self.add_child(EquipmentType(equipment.EquipmentTypes.BOOTS))


class LeatherCap(Armor):
    """
    A composite component representing a Armor item.
    """

    def __init__(self):
        super(LeatherCap, self).__init__()
        self.add_child(Description("Leather Cap",
                                   "An old cap made out of leather, this should keep some harm away."))
        self.add_child(Weight(4))
        self.add_child(GraphicChar(None, colors.ORANGE_D, icon.HELM))
        self.add_child(BlockDamageEquippedEffect(0, 1, [DamageTypes.PHYSICAL]))
        self.add_child(EquipmentType(equipment.EquipmentTypes.HEADGEAR))

class BlockDamageEquippedEffect(EquippedEffect):
    def __init__(self, block, block_variance, blocked_damage_types):
        super(BlockDamageEquippedEffect, self).__init__()
        self.block = block
        self.block_variance = block_variance
        self.blocked_damage_types = blocked_damage_types

    def effect(self, entity):
        """
        Causes the entity that to block some damage.
        """
        entity.add_spoof_child(BlockDamageHealthSpoof(self.block,
                                                      self.block_variance,
                                                      self.blocked_damage_types))


class Sword(Composite):
    """
    A composite component representing a Sword item.
    """

    def __init__(self):
        super(Sword, self).__init__()
        self.add_child(GamePieceType(GamePieceType.ITEM))
        self.add_child(EquipmentType(equipment.EquipmentTypes.MELEE_WEAPON))
        self.add_child(ItemType(ItemType.WEAPON))
        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(Mover())
        self.add_child(Description("Iron Sword",
                                   "This old blade has seen some "
                                   "better days, it's as sharp as "
                                   "ever tough."))
        self.add_child(GraphicChar(None, colors.GRAY, icon.SWORD))
        self.add_child(DamageProvider(6, 3, [DamageTypes.PHYSICAL, DamageTypes.CUTTING]))
        self.add_child(CharPrinter())
        self.add_child(ReEquipAction())
        self.add_child(DropAction())
        self.add_child(PlayerThrowItemAction())
        self.add_child(ThrowerNonBreak())
        self.add_child(Weight(10))
        self.add_child(Hit(16))


class Knife(Sword):
    """
    A composite component representing a Sword item.
    """

    def __init__(self):
        super(Knife, self).__init__()
        self.description.name = "Knife"
        self.description.description = "A trusty knife, small and precise but will only inflict small wounds."
        self.graphic_char.icon = icon.KNIFE
        self.weight.value = 6
        self.hit.value = 21
        self.damage_provider.damage = 3
        self.damage_provider.variance = 1


class Ring(Composite):
    """
    The Ring of Invisibility will make the entity who equips it invisible.
    """

    def __init__(self):
        super(Ring, self).__init__()
        self.add_child(EquipmentType(equipment.EquipmentTypes.RING))
        self.add_child(ItemType(ItemType.JEWELLRY))
        self.add_child(GamePieceType(GamePieceType.ITEM))
        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(Mover())
        self.add_child(GraphicChar(None, colors.YELLOW, icon.RING))
        self.add_child(CharPrinter())
        self.add_child(ReEquipAction())
        self.add_child(DropAction())


class RingOfInvisibility(Ring):
    def __init__(self):
        super(RingOfInvisibility, self).__init__()
        self.graphic_char.color_fg = colors.CYAN
        self.add_child(SetInvisibilityFlagEquippedEffect())
        self.add_child(Description("Ring of Invisibility",
                                   "The metal is warm to your skin, "
                                   "this ring will make you invisible"))


class RingOfEvasion(Ring):
    def __init__(self):
        super(RingOfEvasion, self).__init__()
        self.graphic_char.color_fg = colors.GREEN
        self.add_child(DodgeBonusEquipEffect(3))
        self.add_child(Description("Ring of Evasion",
                                   "The ring is light on your finger, "
                                   "Its magic powers makes it easier for you to dodge attacks."))


class RingOfStealth(Ring):
    def __init__(self):
        super(RingOfStealth, self).__init__()
        self.graphic_char.color_fg = colors.BLUE
        self.add_child(StealthEquipEffect(3))
        self.add_child(Description("Ring of Stealth",
                                   "The ring is smooth to your skin, "
                                   "Its magic powers makes it easier for you to sneak past enemies."))


class RingOfStrength(Ring):
    def __init__(self):
        super(RingOfStrength, self).__init__()
        self.graphic_char.color_fg = colors.ORANGE
        self.add_child(StrengthBonusEquipEffect(3))
        self.add_child(Description("Ring of Strength",
                                   "The ring feels unnaturally heavy, "
                                   "Its magic powers makes you stronger."))

class DodgeBonusEquipEffect(EquippedEffect):
    def __init__(self, dodge_bonus=3):
        super(DodgeBonusEquipEffect, self).__init__()
        self.dodge_bonus = dodge_bonus

    def effect(self, entity):
        """
        Causes the entity that equips this item dodge more often.
        """
        entity.add_spoof_child(DataPointBonusSpoof("evasion", self.dodge_bonus))


class StrengthBonusEquipEffect(EquippedEffect):
    def __init__(self, strength_bonus=3):
        super(StrengthBonusEquipEffect, self).__init__()
        self.strength_bonus = strength_bonus

    def effect(self, entity):
        """
        Causes the entity that equips this item dodge more often.
        """
        entity.add_spoof_child(DataPointBonusSpoof("strength", self.strength_bonus))


class StealthEquipEffect(EquippedEffect):
    def __init__(self, stealth_bonus=3):
        super(StealthEquipEffect, self).__init__()
        self.stealth_bonus = stealth_bonus

    def effect(self, entity):
        """
        Causes the entity that equips this item stealth more often.
        """
        entity.add_spoof_child(DataPointBonusSpoof("stealth", self.stealth_bonus))


class SetInvisibilityFlagEquippedEffect(EquippedEffect):
    def __init__(self):
        super(SetInvisibilityFlagEquippedEffect, self).__init__()

    def effect(self, entity):
        """
        Causes the entity that equips this item to become invisible.
        """
        invisible_flag = entity.StatusFlags.INVISIBILE
        invisibility_effect = entityeffect. \
            StatusAdder(self.parent, self.parent,
                        invisible_flag, time_to_live=1)
        self.parent.effect_queue.add(invisibility_effect)


class HealthPotion(Composite):
    def __init__(self):
        """
        Abstract class, subclasses of this class are potions,
        """
        super(HealthPotion, self).__init__()
        self.add_child(ItemType(ItemType.POTION))
        self.add_child(GamePieceType(GamePieceType.ITEM))
        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(Mover())
        self.add_child(Description("Health Potion",
                                   "An unusual liquid\
                                   contained in a glass flask."))
        self.add_child(GraphicChar(None, colors.PINK, icon.POTION))
        self.add_child(CharPrinter())
        self.add_child(Stacker("health_potion", 3))
        self.add_child(HealingPotionDrinkAction())
        self.add_child(DropAction())

        self.add_child(ThrowerBreak())
        self.add_child(Weight(4))
        self.add_child(PlayerThrowItemAction())


class Weight(Leaf):
    """
    Limits how far the parent item can be thrown.

    A heavier item can't be thrown as far.
    """

    def __init__(self, weight):
        super(Weight, self).__init__()
        self.component_type = "weight"
        self.value = weight


class WeaponRange(Leaf):
    """
    Limits how far the parent weapon can reach.
    """

    def __init__(self, range=5):
        super(WeaponRange, self).__init__()
        self.component_type = "weapon_range"
        self.value = range


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


class HealingPotionDrinkAction(DrinkAction):
    """
    Defines the healing potion drink action.
    """

    def __init__(self):
        super(HealingPotionDrinkAction, self).__init__()
        self.component_type = "health_potion_drink_action"
        self.min_heal = 10
        self.max_heal = 15

    def _drink(self, target_entity):
        """
        When an entity drinks a healing potion, it is healed.
        """
        heal = random.randrange(self.min_heal, self.max_heal + 1)
        heal_effect = entityeffect.Heal(target_entity, heal)
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
            message = "Picked up: " + item.description.name
            messenger.message(message)
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
            messenger.message(message)


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
        damage = Damage(damage_strength, self.variance,
                        self.types, self.parent.hit.value)
        return damage.damage_entity(source_entity, target_entity,
                                    bonus_damage=bonus_damage, bonus_hit=bonus_hit)


class OnUnequipEffect(Leaf):
    """
    Parent items with this component has a effect that happens on equipping.
    """

    def __init__(self, effect_function):
        self.component_type = "on_unequip_effect"
        self.effect = effect_function


class OnEquipEffect(Leaf):
    """
    Parent items with this component has a effect that happens on equipping.
    """

    def __init__(self, effect_function):
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
        messenger.message(message)


class ThrowerBreak(Thrower):
    """
    Items with this component can be thrown, but will survive the fall.
    """

    def __init__(self):
        super(ThrowerBreak, self).__init__()

    def throw_effect(self, dungeon_level, position):
        message = "The " + self.parent.description.name.lower() + \
                  " smashes to the ground and breaks into pieces."
        messenger.message(message)


def _item_flash_animation(entity, item):
    entity.char_printer.append_graphic_char_temporary_frames([item.graphic_char])
