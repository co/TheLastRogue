import colors
import messenger
import action
import gamepiece
import equipment
import entityeffect
import entity


class ItemTypes(object):
    POTION = 0
    WEAPON = 1
    ARMOR = 2
    JEWELLRY = 2
    AMMO = 3

    ALL = [POTION, WEAPON, ARMOR, AMMO]


class Item(gamepiece.GamePiece):
    def __init__(self):
        super(Item, self).__init__()

        self.piece_type = gamepiece.GamePieceType.ITEM
        self.max_instances_in_single_tile = 1

        self.draw_order = 1
        self._name = "XXX_UNNAMED_ITEM_XXX"
        self._description = "XXX_DESCRIPTION_ITEM_XXX"
        self.item_type = None

        self._color_bg = None
        self.inventory = None
        self.actions = []
        self.actions.append(action.DropAction(self))
        self.actions.append(action.PlayerThrowItemAction(self))
        self.weight = 5

    def throw_effect(self, dungeon_level, position):
        self.try_move(position, dungeon_level)
        message = "The " + self.name.lower() +\
            " hits the ground with a thud."
        messenger.messenger.message(message)


class EquipableItem(Item):
    def __init__(self):
        super(EquipableItem, self).__init__()
        self.equipment_type = None

    def equip_effect(self, entity):
        pass

    def unequip_effect(self, entity):
        pass

    def equiped_effect(self, entity):
        pass


class WeaponItem(EquipableItem):
    def __init__(self):
        super(EquipableItem, self).__init__()
        self.item_type = ItemTypes.WEAPON


class MeleeWeapon(WeaponItem):
    def __init__(self):
        super(EquipableItem, self).__init__()
        self.equipment_type = equipment.EquipmentTypes.MELEE_WEAPON


class RangedWeapon(WeaponItem):
    def __init__(self):
        super(EquipableItem, self).__init__()
        self.equipment_type = equipment.EquipmentTypes.RANGED_WEAPON


class JewellryItem(EquipableItem):
    def __init__(self):
        super(EquipableItem, self).__init__()
        self.item_type = ItemTypes.JEWELLRY


class RingItem(JewellryItem):
    def __init__(self):
        super(EquipableItem, self).__init__()
        self.equipment_type = equipment.EquipmentTypes.RING


class RingOfInvisibility(RingItem):
    def __init__(self):
        super(RingOfInvisibility, self).__init__()
        self._color_fg = colors.DB_GOLDEN_FIZZ
        self._symbol = ord('o')
        self._name = "Ring of Invisibility"
        self._description =\
            "The metal is warm to your skin,\
            this ring will make you invisible"
        self.actions.append(action.EquipAction(self))

    def equiped_effect(self, target_entity):
        invisibile_flag = entity.StatusFlags.INVISIBILE
        invisibility_effect = entityeffect.\
            StatusAdder(target_entity, target_entity,
                        invisibile_flag, time_to_live=1)
        target_entity.add_entity_effect(invisibility_effect)


class Gun(RangedWeapon):
    def __init__(self):
        super(Gun, self).__init__()
        self._color_fg = colors.DB_WHITE
        self._symbol = ord('(')
        self._name = "Gun"
        self._description =\
            "This was once a fine weapon, but age has torn it real bad.\n\
            The wooden handle is dry and gray \
            and you see rust eating into the iron pipe."
        self.actions.append(action.EquipAction(self))


class Potion(Item):
    def __init__(self):
        super(Potion, self).__init__()
        self._symbol = ord('?')
        self._name = "XXX_Potion_XXX"
        self._description =\
            "An unusual liquid contained in a glass flask."

    def throw_effect(self, dungeon_level, position):
        message = "The " + self.name.lower() +\
            " smashes to the ground and breaks into pieces."
        messenger.messenger.message(message)


class HealthPotion(Potion):
    def __init__(self):
        super(Potion, self).__init__()
        self._color_fg = colors.DB_PLUM
        self._name = "Health Potion"
        self._description =\
            "An unusual liquid contained in a glass flask."
        self.actions.append(action.HealingPotionDrink(self))
