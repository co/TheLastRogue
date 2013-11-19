import random

from action import Action
from compositecore import Leaf, Composite
from attacker import Damage, DamageTypes
from graphic import GraphicChar, CharPrinter
from health import BlockDamageHealthSpoof
from missileaction import PlayerThrowItemAction
from mover import Mover
from position import Position, DungeonLevel
from stats import GamePieceType, Hit
from text import Description
import action
import colors
import entityeffect
import equipment
import gametime
from messenger import messenger
import icon


class ItemType(Leaf):
    """
    Enumerator class denoting different item types. Inventory is sorted on ItemType.
    """
    POTION = 0
    WEAPON = 1
    ARMOR = 2
    JEWELLRY = 3
    AMMO = 4

    ALL = [POTION, WEAPON, ARMOR, AMMO]

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
        self.add_child(GraphicChar(None, colors.GRAY, ":"))
        self.add_child(DropAction())
        self.add_child(CharPrinter())
        self.add_child(Weight(1))
        self.add_child(Hit(17))


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
        self.add_child(EquipmentType(equipment.EquipmentTypes.ARMOR))
        self.add_child(ItemType(ItemType.ARMOR))
        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(Mover())
        self.add_child(Description("Leather Armor",
                                   "A worn leather armor, "
                                   "it's old, but should still "
                                   "protect you from some damage."))
        self.add_child(GraphicChar(None, colors.ORANGE_D, icon.ARMOR))
        self.add_child(BlockDamageEquippedEffect(5, 3,
                                                 [DamageTypes.PHYSICAL]))
        self.add_child(CharPrinter())
        self.add_child(ReEquipAction())
        self.add_child(DropAction())
        self.add_child(PlayerThrowItemAction())
        self.add_child(ThrowerNonBreak())
        self.add_child(Weight(10))


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
        entity.add_spoof_child(BlockDamageHealthSpoof
                               (self.block,
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
                                   "This old blade has seen some, "
                                   "better days, it's as sharp as "
                                   "tough."))
        self.add_child(GraphicChar(None, colors.GRAY, icon.SWORD))
        self.add_child(DamageProvider(10, 3, [DamageTypes.PHYSICAL,
                                              DamageTypes.CUTTING]))
        self.add_child(CharPrinter())
        self.add_child(ReEquipAction())
        self.add_child(DropAction())
        self.add_child(PlayerThrowItemAction())
        self.add_child(ThrowerNonBreak())
        self.add_child(Weight(10))
        self.add_child(Hit(17))


class RingOfInvisibility(Leaf):
    """
    The Ring of Invisibility will make the entity who equips it invisible.
    """
    def __init__(self):
        super(RingOfInvisibility, self).__init__()
        self.add_child(EquipmentType(equipment.EquipmentTypes.RING))
        self.add_child(ItemType(ItemType.JEWELLRY))
        self.add_child(GamePieceType(GamePieceType.ITEM))
        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(Mover())
        self.add_child(Description("Ring of Invisibility",
                                   "The metal is warm to your skin, "
                                   "this ring will make you invisible"))
        self.add_child(GraphicChar(None, colors.YELLOW, icon.RING))
        self.add_child(CharPrinter())
        self.add_child(ReEquipAction())
        self.add_child(DropAction())
        self.add_child(EquippedEffect(SetInvisibilityFlagEquippedEffect()))


class SetInvisibilityFlagEquippedEffect(EquippedEffect):
    def __init__(self):
        super(SetInvisibilityFlagEquippedEffect, self).__init__()

    def effect(self, entity):
        """
        Causes the entity that equips this item to become invisible.
        """
        invisibile_flag = entity.StatusFlags.INVISIBILE
        invisibility_effect = entityeffect.\
            StatusAdder(self.parent, self.parent,
                        invisibile_flag, time_to_live=1)
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
            drop_successful =\
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
        if(action.EQUIPMENT_SLOT in kwargs):
            equipment_slot = kwargs[action.EQUIPMENT_SLOT]
        else:
            equipment_slot = self.get_equipment_slot(source_entity)
        old_item = None
        if(source_entity.equipment.slot_is_equiped(equipment_slot)):
            old_item = source_entity.equipment.unequip(equipment_slot)
        self._re_equip(source_entity, equipment_slot)
        if(not old_item is None):
            source_entity.inventory.try_add(old_item)
        self.add_energy_spent_to_entity(source_entity)

    def get_equipment_slot(self, source_entity):
        """
        Finds the right equipment slot.
        """
        open_slots = (source_entity.equipment.get_open_slots_of_type
                      (self.parent.equipment_type.value))
        if(len(open_slots) > 0):
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
        re_equip_effect =\
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
        self.min_health = 5
        self.max_health = 10

    def _drink(self, target_entity):
        """
        When an entity drinks a healing potion, it is healed.
        """
        health = random.randrange(self.min_health, self.max_health)
        heal_effect = entityeffect.Heal(target_entity, health)
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
        print "time to pickup", item
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
        if(not item is None and
           not self.parent.inventory.has_room_for_item(item)):
            message = "Could not pick up: " + item.description.name +\
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

    def damage_entity(self, source_entity, target_entity):
        self._damage = Damage(self.damage, self.variance,
                              self.types, self.parent.hit.value)
        return self._damage.damage_entity(source_entity, target_entity)


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
        message = "The " + self.parent.description.name.lower() +\
            " hits the ground with a thud."
        messenger.message(message)


class ThrowerBreak(Thrower):
    """
    Items with this component can be thrown, but will survive the fall.
    """
    def __init__(self):
        super(ThrowerBreak, self).__init__()

    def throw_effect(self, dungeon_level, position):
        message = "The " + self.parent.description.name.lower() +\
            " smashes to the ground and breaks into pieces."
        messenger.message(message)
