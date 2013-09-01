import colors
import symbol
import damage
import messenger
import action
import missileaction
import gamepiece
import equipment
import entityeffect
import entity


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


class Item(gamepiece.GamePiece):
    """
    Abstract class representing an item in the game.

    piece_type (GamePieceType): Denotes that Item and all its
                                subclasses is of type ITEM.
    max_instances_in_single_tile: The number of allowed pieces of this types
                                  on a tile.
    item_type (ItemType): Denotes the type of item it is, should be provided
                          by the subclasses.

    inventory (Inventory): If this item is in an entities inventory this
                           field should be point to that inventory
                           otherwise it shall be None.
    actions (list of Action): A list of player actions the player
                              can do with this item.

    weight (int): The Weight of the item.
    """
    def __init__(self):
        super(Item, self).__init__()

        self.piece_type = gamepiece.GamePieceType.ITEM
        self.max_instances_in_single_tile = 1

        self._name = "XXX_UNNAMED_ITEM_XXX"
        self._description = "XXX_DESCRIPTION_ITEM_XXX"
        self.item_type = None
        self.equipment_type = None

        self._color_bg = None
        self.inventory = None
        self.actions = []
        self.actions.append(action.DropAction(self))
        self.actions.append(missileaction.PlayerThrowItemAction(self))
        self.weight = 5

    def throw_effect(self, dungeon_level, position):
        """
        The effect of throwing this item.

        dungeon_level: The DungeonLevel the throw was performed on.
        position: The point at which the item hits the ground.
        """
        self.try_move(position, dungeon_level)
        message = "The " + self.name.lower() +\
            " hits the ground with a thud."
        messenger.messenger.message(message)

    def _can_pass_terrain(self, terrain_to_pass):
        if(terrain_to_pass is None):
            return False
        return not terrain_to_pass.is_solid()


class StackAbleItem(Item):
    """
    Abstract class, subclasses of this class is stackaple in entity inventory.
    """
    def __init__(self):
        super(StackAbleItem, self).__init__()
        self.quantity = 1


class EquipableItem(Item):
    """
    Abstract class, subclasses of this class is equipable.
    """
    def __init__(self):
        super(EquipableItem, self).__init__()
        self.actions.append(action.ReEquipAction(self))

    """
    Effect that will happen the entity that equips this item.
    Will be called on equip.
    """
    def equip_effect(self, entity):
        pass

    """
    Effect that will happen the entity that un-equips this item.
    Will be called on un-equip.
    """
    def unequip_effect(self, entity):
        pass

    """
    Effect that will happen while this item is equiped.
    Will be called each tick this item is equiped.
    """
    def equiped_effect(self, entity):
        pass


class WeaponItem(EquipableItem):
    """
    Abstract class, subclasses of this class are of ItemType WEAPON.
    """
    def __init__(self):
        super(WeaponItem, self).__init__()
        self.item_type = ItemType.WEAPON
        self._damage_strength = 0
        self._damage_variance = 0
        self._damage_types = []

    @property
    def damage(self):
        return damage.Damage(self._damage_strength, self._damage_variance,
                             self._damage_types)


class MeleeWeapon(WeaponItem):
    """
    Abstract class, subclasses of this class are melee weapons
    and fits in the melee weapon equipment slot.
    """
    def __init__(self):
        super(MeleeWeapon, self).__init__()
        self.equipment_type = equipment.EquipmentTypes.MELEE_WEAPON


class RangedWeapon(WeaponItem):
    """
    Abstract class, subclasses of this class are ranged weapons
    and fits in the ranged weapon equipment slot.

    weapon_range (int): Distance the weapon can fire.
    """
    def __init__(self):
        super(RangedWeapon, self).__init__()
        self.equipment_type = equipment.EquipmentTypes.RANGED_WEAPON
        self.weapon_range = 0


class Gun(RangedWeapon):
    """
    Non-abstract ranged weapon item class.
    """
    def __init__(self):
        super(Gun, self).__init__()
        self.gfx_char.color_fg = colors.WHITE
        self.gfx_char.symbol = symbol.GUN
        self._name = "Gun"
        self._description =\
            "This was once a fine weapon, but age has torn it real bad.\n\
            The wooden handle is dry and gray, \
            you see rust eating into the iron pipe."

        self._damage_strength = 10
        self._damage_variance = 5
        self._damage_types = [damage.DamageTypes.PHYSICAL,
                              damage.DamageTypes.PIERCING]

        self.weapon_range = 15


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
