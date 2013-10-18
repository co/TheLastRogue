import colors
from gamepiecetype import GamePieceType
from position import Position
from dungeonlevelcomposite import DungeonLevel
from composite import Description, GraphicChar, CharPrinter
import gametime
import random
import symbol
import damage
import messenger
import action
from action import Action
import equipment
import entityeffect
import entity
from compositecore import Leaf


class ItemType(object):
    """
    Enumerator class denoting different item types.
    """
    POTION = 0
    WEAPON = 1
    ARMOR = 2
    JEWELLRY = 3
    AMMO = 4

    ALL = [POTION, WEAPON, ARMOR, AMMO]

#
#class Item(gamepiece.GamePiece):
#    """
#    Abstract class representing an item in the game.
#
#    Attributes:
#        piece_type (GamePieceType): Denotes that Item and all its
#                                    subclasses are of type ITEM.
#        max_instances_in_single_tile: The number of allowed pieces of this
#                                      types on a tile.
#        item_type (ItemType): Denotes the type of item it is, should be
#                              provided by the subclasses.
#
#        inventory (Inventory): If this item is in an entities inventory this
#                            field should be point to that inventory
#                            otherwise it shall be None.
#        actions (list of Action): A list of player actions the player
#                                can do with this item.
#
#        weight (int): The Weight of the item.
#    """
#    def __init__(self):
#        super(Item, self).__init__()
#
#        self.piece_type = gamepiece.GamePieceType.ITEM
#        self.max_instances_in_single_tile = 1
#
#        self._name = "XXX_UNNAMED_ITEM_XXX"
#        self._description = "XXX_DESCRIPTION_ITEM_XXX"
#        self.item_type = None
#        self.equipment_type = None
#
#        self._color_bg = None
#        self.inventory = None
#        self.actions = []
#        self.actions.append(action.DropAction(self))
#        self.actions.append(missileaction.PlayerThrowItemAction(self))
#        self.weight = 5
#
#    def throw_effect(self, dungeon_level, position):
#        """
#        The effect of throwing this item.
#
#        dungeon_level: The DungeonLevel the throw was performed on.
#        position: The point at which the item hits the ground.
#        """
#        self.try_move(position, dungeon_level)
#        message = "The " + self.name.lower() +\
#            " hits the ground with a thud."
#        messenger.messenger.message(message)
#
#    def _can_pass_terrain(self, terrain_to_pass):
#        if(terrain_to_pass is None):
#            return False
#        return not terrain_to_pass.is_solid()


class Weight(Leaf):
    """
    Limits how far the parent item can be thrown.

    A heavier item can't be thrown as far.
    """
    def __init__(self, weight=10):
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

    def act(self, **kwargs):
        """
        The action that this component defines.
        """
        pass

    def can_act(self, **kwargs):
        """
        Returns true if it is valid to call the act method.
        """
        return True

    def add_energy_spent_to_entity(self, entity):
        """
        Help method for spending energy for the act performing entity.
        """
        entity.newly_spent_energy += self.energy_cost

    def copy(self):
        """
        Copy function.
        """
        result = self.__class__()
        return result


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
        if(not self.parent.inventory is None):
            drop_successful =\
                self.parent.inventory.try_drop_item(self.parent)
            if(drop_successful):
                self.add_energy_spent_to_entity(source_entity)
        return


class ThrowAction(Action):
    """
    An entity holding the parent item in its inventory should be able to throw
    the item using this action.
    """
    def __init__(self):
        super(ThrowAction,
              self).__init__()
        self.component_type = "throw_action"


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
            entityeffect.ReEquip(target_entity, target_entity,
                                 equipment_slot, self.parent)
        target_entity.add_entity_effect(re_equip_effect)
        target_entity.inventory.remove_item(self.parent)


class UnEquipAction(Action):
    """
    An Item with this component can be unequipped.

    If an item is already in that
    equipment slot that item will be unequipped first.
    """
    def __init__(self):
        super(UnEquipAction, self).__init__()
        self.component_type = "unequip_action"
        self.name = "Remove"
        self.display_order = 90

    def act(self, **kwargs):
        """
        Will attempt to unequip item to the given equipment_slot.
        """
        target_entity = kwargs[action.TARGET_ENTITY]
        source_entity = kwargs[action.SOURCE_ENTITY]
        equipment_slot = kwargs[action.EQUIPMENT_SLOT]
        if(not self.parent is None):
            self._unequip(target_entity, equipment_slot)
            self.add_energy_spent_to_entity(source_entity)

    def can_act(self, **kwargs):
        """
        Returns true if it's legal for the entity to unequip item.
        """
        source_entity = kwargs[action.SOURCE_ENTITY]
        equipment_slot = kwargs[action.EQUIPMENT_SLOT]
        return (source_entity.inventory.has_room_for_item() and
                source_entity.equipment.slot_is_equiped(equipment_slot))

    def _unequip(self, target_entity, equipment_slot):
        """
        Performs the actual unequip.
        """
        if(not target_entity.equipment.slot_is_equiped(equipment_slot)):
            return
        unequip_effect = entityeffect.UnEquip(target_entity,
                                              target_entity, equipment_slot)
        target_entity.add_entity_effect(unequip_effect)


class DrinkAction(Action):
    """
    Abstract class, drink actions should inherit from this class.
    """
    def __init__(self, source_item):
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
        self.remove_from_inventory()
        self.add_energy_spent_to_entity(source_entity)

    def _drink(self):
        """
        The drink action subclasses should override
        and define the drink action here.
        """
        pass


class HealingPotionDrink(DrinkAction):
    """
    Defines the healing potion drink action.
    """
    def __init__(self, source_item):
        super(HealingPotionDrink, self).__init__(source_item)
        self.component_type = "health_potion_drink_action"
        self.min_health = 5
        self.max_health = 10

    def drink(self, target_entity):
        """
        When an entity drinks a healing potion, it is healed.
        """
        health = random.randrange(self.min_health, self.max_health)
        heal_effect = entityeffect.Heal(target_entity, target_entity, health)
        target_entity.add_entity_effect(heal_effect)


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
                source_entity.inventory.has_room_for_item())

    def act(self, **kwargs):
        """
        Performs the pickup action.
        """
        source_entity = kwargs[action.SOURCE_ENTITY]
        item = self._get_item_on_floor(source_entity)
        pickup_succeded = source_entity.inventory.try_add(item)
        if(pickup_succeded):
            message = "Picked up: " + item.name
            messenger.messenger.message(message)
            source_entity.newly_spent_energy += gametime.single_turn

    def _get_item_on_floor(self, entity):
        return entity.dungeon_level.get_tile(entity.position).get_first_item()

    def print_player_error(self, **kwargs):
        """
        Prints a message to the user explaining what went wrong.
        """
        source_entity = kwargs[action.SOURCE_ENTITY]
        item = self._get_item_on_floor(source_entity)
        if(item is None and
           not source_entity.inventory.has_room_for_item()):
            message = "Could not pick up: " + item.name +\
                ", the inventory is full."
            messenger.messenger.message(message)


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
    The provides a way for the parent calculate damage.
    """
    def __init__(self, damage, variance, types):
        super(EquipmentType, self).__init__()
        self.component_type = "equipment_type"
        self._strength = damage
        self._variance = variance
        self._types = types


class OnEquipEffect(Leaf):
    """
    Parent items with this component has a effect that happens on equiping.
    """
    def __init__(self, effect_function):
        self.component_type = "on_equip_effect"
        self.effect = effect_function

#class StackAbleItem(Item):
#    """
#    Abstract class, subclasses of this class is stackaple in entity inventory.
#    """
#    def __init__(self):
#        super(StackAbleItem, self).__init__()
#        self.quantity = 1
#
#
#class EquipableItem(Item):
#    """
#    Abstract class, subclasses of this class is equipable.
#    """
#    def __init__(self):
#        super(EquipableItem, self).__init__()
#        self.actions.append(action.ReEquipAction(self))
#
#    """
#    Effect that will happen the entity that equips this item.
#    Will be called on equip.
#    """
#    def equip_effect(self, entity):
#        pass
#
#    """
#    Effect that will happen the entity that un-equips this item.
#    Will be called on un-equip.
#    """
#    def unequip_effect(self, entity):
#        pass
#
#    """
#    Effect that will happen while this item is equiped.
#    Will be called each tick this item is equiped.
#    """
#    def equiped_effect(self, entity):
#        pass


#class WeaponItem(EquipableItem):
#    """
#    Abstract class, subclasses of this class are of ItemType WEAPON.
#    """
#    def __init__(self):
#        super(WeaponItem, self).__init__()
#        self.item_type = ItemType.WEAPON
#        self._damage_strength = 0
#        self._damage_variance = 0
#        self._damage_types = []
#
#    @property
#    def damage(self):
#        return damage.Damage(self._damage_strength, self._damage_variance,
#                             self._damage_types)
#
#
#class MeleeWeapon(WeaponItem):
#    """
#    Abstract class, subclasses of this class are melee weapons
#    and fits in the melee weapon equipment slot.
#    """
#    def __init__(self):
#        super(MeleeWeapon, self).__init__()
#        self.equipment_type = equipment.EquipmentTypes.MELEE_WEAPON
#
#
#class RangedWeapon(WeaponItem):
#    """
#    Abstract class, subclasses of this class are ranged weapons
#    and fits in the ranged weapon equipment slot.
#
#    weapon_range (int): Distance the weapon can fire.
#    """
#    def __init__(self):
#        super(RangedWeapon, self).__init__()
#        self.equipment_type = equipment.EquipmentTypes.RANGED_WEAPON
#        self.weapon_range = 0
#

class Gun(Leaf):
    """
    A composite component representing a Gun item.
    """
    def __init__(self):
        super(Gun, self).__init__()
        self.add_child(GamePieceType(GamePieceType.ITEM))
        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(Description("Gun",
                                   "This was once a fine weapon, \
                                   but age has torn it real bad.\n\
                                   The wooden handle is dry and gray, \
                                   you see rust eating into the iron pipe."))
        self.add_child(GraphicChar(None, colors.WHITE,
                                   symbol.GUN))
        self.add_child(CharPrinter())
        self.add_child(DamageProvider(10, 5, [damage.DamageTypes.PHYSICAL,
                                              damage.DamageTypes.PIERCING]))
        self.add_child(WeaponRange(15))


class JewellryItem(EquipableItem):
    """
    Abstract class, subclasses of this class are of ItemType JEWELLRY.
    """
    def __init__(self):
        super(JewellryItem, self).__init__()
        self.item_type = ItemType.JEWELLRY


class RingItem(JewellryItem):
    """
    Abstract class, subclasses of this class are rings
    and fits in the ring equipment slots.
    """
    def __init__(self):
        super(RingItem, self).__init__()
        self.equipment_type = equipment.EquipmentTypes.RING
        self.gfx_char.symbol = symbol.RING


class RingOfInvisibility(RingItem):
    """
    Non-abstract ranged ring item class,
    instance items will make the user entity invisible.
    """
    def __init__(self):
        super(RingOfInvisibility, self).__init__()
        self.gfx_char.color_fg = colors.YELLOW
        self._name = "Ring of Invisibility"
        self._description =\
            "The metal is warm to your skin,\
            this ring will make you invisible"

    def equiped_effect(self, target_entity):
        """
        Causes the entity that equips this item to become invisible.
        """
        invisibile_flag = entity.StatusFlags.INVISIBILE
        invisibility_effect = entityeffect.\
            StatusAdder(target_entity, target_entity,
                        invisibile_flag, time_to_live=1)
        target_entity.add_entity_effect(invisibility_effect)


class Potion(StackAbleItem):
    def __init__(self):
        """
        Abstract class, subclasses of this class are potions,
        """
        super(Potion, self).__init__()
        self.gfx_char.symbol = symbol.POTION
        self._name = "XXX_Potion_XXX"
        self._description =\
            "An unusual liquid contained in a glass flask."

    def throw_effect(self, dungeon_level, position):
        message = "The " + self.name.lower() +\
            " smashes to the ground and breaks into pieces."
        messenger.messenger.message(message)


class HealthPotion(Potion):
    """
    Health Potions are potion that heals entities.
    """
    def __init__(self):
        super(HealthPotion, self).__init__()
        self.gfx_char.color_fg = colors.PINK
        self._name = "Health Potion"
        self._description =\
            "An unusual liquid contained in a glass flask."
        self.actions.append(action.HealingPotionDrink(self))


class Ammo(StackAbleItem):
    """
    Gun bullets, are needed to fire guns.
    """
    def __init__(self):
        super(Ammo, self).__init__()
        self.gfx_char.color_fg = colors.GRAY
        self.gfx_char.symbol = ":"
        self._name = "Ammunition"
        self._description =\
            "Rounds for a gun."
