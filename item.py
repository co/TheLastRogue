import random
from Status import DAMAGE_REFLECT_STATUS_ICON, LIFE_STEAL_STATUS_ICON

from action import Action
from actor import DoNothingActor
from cloud import new_steam_cloud, new_explosion_cloud, new_poison_cloud, new_fire_cloud
from compositecommon import PoisonEntityEffectFactory
from compositecore import Leaf, Composite
from attacker import Attack, DamageTypes
import direction
from dummyentities import dummy_flyer
import geometry
from graphic import GraphicChar, CharPrinter
from health import ReflectDamageTakenEffect
import messenger
from missileaction import PlayerThrowItemAction
from monster import HealAnEntityOnDeath, AddEffectToOtherSeenEntities
from mover import Mover
from position import Position, DungeonLevel
import rng
from shapegenerator import extend_points
from stats import DataPointBonusSpoof, DataPoint, Flag, DataTypes, GamePieceTypes
from statusflags import StatusFlags
from terrain import GlassWall
from text import Description
import action
import colors
import entityeffect
import equipment
import gametime
from messenger import msg
import icon
from util import entity_skip_turn


class ItemType(Leaf):
    """
    Enumerator class denoting different item types. Inventory is sorted on ItemType.
    """
    POTION = 0
    SCROLL = 1
    BOMB = 2
    MACHINE = 3
    WEAPON = 4
    ARMOR = 5
    JEWELLRY = 6
    AMMO = 7

    ALL = [POTION, BOMB, MACHINE, WEAPON, ARMOR, JEWELLRY, AMMO]

    def __init__(self, item_type):
        super(ItemType, self).__init__()
        self.component_type = "item_type"
        self.value = item_type


def set_item_components(item, game_state):
    item.set_child(Position())
    item.set_child(DoNothingActor())
    item.set_child(DungeonLevel())
    item.set_child(Mover())
    item.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.ITEM))
    item.set_child(DataPoint(DataTypes.GAME_STATE, game_state))
    item.set_child(CharPrinter())
    item.set_child(DropAction())
    item.set_child(PlayerThrowItemAction())
    item.set_child(ThrowerNonBreak())
    return item


def set_ranged_weapon_components(item):
    item.set_child(EquipmentType(equipment.EquipmentTypes.RANGED_WEAPON))
    item.set_child(ItemType(ItemType.WEAPON))
    item.set_child(ReEquipAction())


def new_gun(game_state):
    gun = Composite()
    set_item_components(gun, game_state)
    set_ranged_weapon_components(gun)
    gun.set_child(RangeWeaponType(RangeWeaponType.GUN))
    gun.set_child(Description("Gun",
                              "This was once a fine weapon, \
                               but age has torn it real bad.\n\
                               The wooden handle is dry and gray, \
                               you see rust eating into the iron pipe."))
    gun.set_child(GraphicChar(None, colors.WHITE, icon.GUN))
    gun.set_child(AttackProvider(15, 10, [DamageTypes.PHYSICAL,
                                          DamageTypes.PIERCING]))
    gun.set_child(DataPoint(DataTypes.WEAPON_RANGE, 15))
    gun.set_child(DataPoint(DataTypes.HIT, 13))
    gun.set_child(DataPoint(DataTypes.WEIGHT, 5))
    return gun


def new_sling(game_state):
    sling = Composite()
    set_item_components(sling, game_state)
    set_ranged_weapon_components(sling)
    sling.set_child(RangeWeaponType(RangeWeaponType.SLING))
    sling.set_child(Description("Sling",
                                "This weapon propels rocks more effectively than throwing them would."))
    sling.set_child(GraphicChar(None, colors.ORANGE, icon.SLING))
    sling.set_child(DataPoint(DataTypes.WEAPON_RANGE, 4))
    sling.set_child(AttackProvider(1, 2, [DamageTypes.PHYSICAL, DamageTypes.PIERCING]))
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


def new_darkness_device(game_state):
    device = Composite()
    set_item_components(device, game_state)
    set_device_components(device)
    device.set_child(Description("Device of Darkness",
                                 "This ancient device will dim the vision of all creatures on the floor."))
    device.set_child(DarknessDeviceAction())
    device.set_child(GraphicChar(None, colors.GREEN, icon.MACHINE))
    return device


def new_heart_stop_device(game_state):
    device = Composite()
    set_item_components(device, game_state)
    set_device_components(device)
    device.set_child(Description("Dev. of Heart Stop",
                                 "This ancient device will cause a random creature on the floor to have a heart attack."))
    device.set_child(HeartStopDeviceAction())
    device.set_child(GraphicChar(None, colors.BLUE, icon.MACHINE))
    return device


def new_glass_device(game_state):
    device = Composite()
    set_item_components(device, game_state)
    set_device_components(device)
    device.set_child(Description("Dev. of Glassmaking",
                                 "This ancient device will turn all nearby stone into glass."))
    device.set_child(GlassDeviceAction())
    device.set_child(GraphicChar(None, colors.CYAN, icon.MACHINE))
    return device


def new_swap_device(game_state):
    device = Composite()
    set_item_components(device, game_state)
    set_device_components(device)
    device.set_child(Description("Device of Swaping",
                                 "This ancient device will swap places with every creature in view."))
    device.set_child(SwapDeviceAction())
    device.set_child(GraphicChar(None, colors.YELLOW, icon.MACHINE))
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
        ttl = gametime.single_turn * rng.random_variance(10, 5)
        entities = source_entity.dungeon_level.value.entities
        msg.send_global_message(messenger.DARKNESS_MESSAGE)
        for entity in entities:
            sight_radius_spoof = DataPoint(DataTypes.SIGHT_RADIUS, 1)
            darkness_effect = entityeffect.AddSpoofChild(source_entity, sight_radius_spoof, time_to_live=ttl)
            entity.effect_queue.add(darkness_effect)


class GlassDeviceAction(ActivateDeviceAction):
    def __init__(self):
        super(GlassDeviceAction, self).__init__()
        self.component_type = "glass_device_activate_action"

    def _turn_to_glass_if_wall(self, position, dungeon_level):
        terrain = dungeon_level.get_tile(position).get_terrain()
        if terrain.has("is_wall"):
            glass_wall = GlassWall()
            glass_wall.mover.replace_move(position, dungeon_level)
            return True
        return False

    def _activate(self, source_entity):
        sight_radius = source_entity.sight_radius.value
        dungeon_level = source_entity.dungeon_level.value
        top = source_entity.position.value[1] - sight_radius
        left = source_entity.position.value[0] - sight_radius
        turned_something_to_glass = False
        for x in range(left, left + 2 * sight_radius + 1):
            for y in range(top, top + 2 * sight_radius + 1):
                try:
                    turned_something_to_glass = self._turn_to_glass_if_wall((x, y), dungeon_level)
                except IndexError:
                    continue
        if turned_something_to_glass:
            dungeon_level.signal_terrain_changed()
            msg.send_global_message(messenger.GLASS_TURNING_MESSAGE)


class SwapDeviceAction(ActivateDeviceAction):
    def __init__(self):
        super(SwapDeviceAction, self).__init__()
        self.component_type = "swap_device_activate_action"

    def _activate(self, source_entity):
        dungeon_level = source_entity.dungeon_level.value
        entities_in_sight = source_entity.vision.get_seen_entities()
        entities_in_sight.append(source_entity)

        positions = [e.position.value for e in entities_in_sight]
        random.shuffle(positions)

        for entity in entities_in_sight:
            entity.mover.try_remove_from_dungeon()

        for entity in entities_in_sight:
            print positions
            entity.mover.try_move(positions.pop(), dungeon_level)
        msg.send_global_message(messenger.GLASS_TURNING_MESSAGE)


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


def new_ammunition(game_state):
    """
    A composite component representing a gun ammunition item.
    """
    ammo = Composite()
    set_item_components(ammo, game_state)
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
        self.component_type = "equipped_effect"  #TODO: should be tag to allow multiple effects?

    def effect(self, entity):
        pass


def set_armor_components(item):
    item.set_child(ItemType(ItemType.ARMOR))
    item.set_child(ReEquipAction())
    return item


def new_leather_armor(game_state):
    """
    A composite component representing a Armor item.
    """
    armor = Composite()
    set_item_components(armor, game_state)
    set_armor_components(armor)
    armor.set_child(Description("Leather Armor",
                                "A worn leather armor. It's old, but should still protect you from some damage."))
    armor.set_child(GraphicChar(None, colors.ORANGE_D, icon.ARMOR))
    armor.set_child(StatBonusEquipEffect("armor", 2))
    armor.set_child(EquipmentType(equipment.EquipmentTypes.ARMOR))
    armor.set_child(DataPoint(DataTypes.WEIGHT, 10))
    return armor


def new_leather_boots(game_state):
    """
    A composite component representing a Boots Armor item.
    """
    boots = Composite()
    set_item_components(boots, game_state)
    set_armor_components(boots)
    boots.set_child(Description("Leather Boots",
                                "A worn pair of boots, dry mud covers most of the leather."))
    boots.set_child(DataPoint(DataTypes.WEIGHT, 4))
    boots.set_child(GraphicChar(None, colors.ORANGE_D, icon.BOOTS))
    boots.set_child(StatBonusEquipEffect("armor", 1))
    boots.set_child(EquipmentType(equipment.EquipmentTypes.BOOTS))
    return boots


def new_leather_cap(game_state):
    """
    A composite component representing a Armor item.
    """
    cap = Composite()
    set_item_components(cap, game_state)
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


def new_sword(game_state):
    """
    A composite component representing a Sword item.
    """
    sword = Composite()
    set_item_components(sword, game_state)
    set_melee_weapon_component(sword)
    sword.set_child(Description("Iron Sword",
                                "This old blade has seen some better days, it's as sharp as ever tough."))
    sword.set_child(GraphicChar(None, colors.GRAY, icon.SWORD))
    sword.set_child(AttackProvider(4, 1, [DamageTypes.PHYSICAL, DamageTypes.CUTTING]))
    sword.set_child(DataPoint(DataTypes.WEIGHT, 10))
    sword.set_child(DataPoint(DataTypes.HIT, 17))
    return sword


def new_mace(game_state):
    """
    A composite component representing a Sword item.
    """
    mace = Composite()
    set_item_components(mace, game_state)
    set_melee_weapon_component(mace)
    mace.set_child(Description("Iron Mace",
                                "This old club has an lump of iron at one end."))
    mace.set_child(GraphicChar(None, colors.GRAY, icon.MACE))
    mace.set_child(AttackProvider(3, 1, [DamageTypes.PHYSICAL, DamageTypes.BLUNT]))
    mace.set_child(DataPoint(DataTypes.WEIGHT, 8))
    mace.set_child(DataPoint(DataTypes.HIT, 16))
    mace.set_child(StunAttackEffect(1.0))
    return mace


def new_knife(game_state):
    """
    A composite component representing a Knife item.
    """
    knife = Composite()
    set_item_components(knife, game_state)
    set_melee_weapon_component(knife)
    knife.set_child(Description("Knife", "A trusty knife, small and precise but will only inflict small wounds."))
    knife.set_child(GraphicChar(None, colors.GRAY, icon.KNIFE))
    knife.set_child(AttackProvider(2, 1, [DamageTypes.PHYSICAL, DamageTypes.CUTTING]))
    knife.set_child(DataPoint(DataTypes.WEIGHT, 5))
    knife.set_child(DataPoint(DataTypes.HIT, 21))
    return knife


def set_ring_components(item):
    item.set_child(EquipmentType(equipment.EquipmentTypes.RING))
    item.set_child(ItemType(ItemType.JEWELLRY))
    item.set_child(ReEquipAction())
    item.set_child(DataPoint(DataTypes.WEIGHT, 2))


def set_amulet_components(item):
    item.set_child(EquipmentType(equipment.EquipmentTypes.AMULET))
    item.set_child(ItemType(ItemType.JEWELLRY))
    item.set_child(ReEquipAction())
    item.set_child(DataPoint(DataTypes.WEIGHT, 3))


def new_ring_of_invisibility(game_state):
    ring = Composite()
    set_item_components(ring, game_state)
    set_ring_components(ring)
    ring.set_child(GraphicChar(None, colors.CYAN, icon.RING))
    ring.set_child(SetInvisibilityFlagEquippedEffect())
    ring.set_child(Description("Ring of Invisibility",
                               "The metal is warm to your skin, "
                               "this ring will make you invisible"))
    return ring


def new_ring_of_evasion(game_state):
    ring = Composite()
    set_item_components(ring, game_state)
    set_ring_components(ring)
    ring.set_child(GraphicChar(None, colors.GREEN, icon.RING))
    ring.set_child(StatBonusEquipEffect("evasion", 3))
    ring.set_child(Description("Ring of Evasion",
                               "The ring is light on your finger, "
                               "Its magic powers makes it easier for you to dodge attacks."))
    return ring


def new_ring_of_stealth(game_state):
    ring = Composite()
    set_item_components(ring, game_state)
    set_ring_components(ring)
    ring.set_child(GraphicChar(None, colors.BLUE, icon.RING))
    ring.set_child(StatBonusEquipEffect("stealth", 3))
    ring.set_child(Description("Ring of Stealth",
                               "The ring is smooth to your skin, "
                               "Its magic powers makes it easier for you to sneak past enemies."))
    return ring


def new_ring_of_strength(game_state):
    ring = Composite()
    set_item_components(ring, game_state)
    set_ring_components(ring)
    ring.set_child(GraphicChar(None, colors.ORANGE, icon.RING))
    ring.set_child(StatBonusEquipEffect("strength", 3))
    ring.set_child(Description("Ring of Strength",
                               "The ring feels unnaturally heavy, "
                               "Its magic powers makes you stronger."))
    return ring


def new_amulet_of_reflect_damage(game_state):
    amulet = Composite()
    set_item_components(amulet, game_state)
    set_amulet_components(amulet)
    amulet.set_child(GraphicChar(None, colors.CYAN, icon.AMULET))
    amulet.set_child(AddSpoofChildEquipEffect(ReflectDamageTakenEffect,
                                              DAMAGE_REFLECT_STATUS_ICON))
    amulet.set_child(Description("Amulet of Reflection",
                                 "The amulet feels cold and heavy,"
                                 "it is made of enchanted silver, "
                                 "Its magic powers will damage those who hurt you."))
    return amulet


def new_amulet_of_life_steal(game_state):
    amulet = Composite()
    set_item_components(amulet, game_state)
    set_amulet_components(amulet)
    amulet.set_child(GraphicChar(None, colors.RED, icon.AMULET))
    amulet.set_child(LifeStealEffect())
    amulet.set_child(Description("Amulet of the Nosferatu",
                                 "The gem at the center pulsates when blood is near."
                                 "Its magic powers will heal you see a creature die."))
    return amulet


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


class AddSpoofChildEquipEffect(EquippedEffect):
    def __init__(self, spoof_child_factory, status_icon=None):
        super(AddSpoofChildEquipEffect, self).__init__()
        self.spoof_child_factory = spoof_child_factory
        self.status_icon = status_icon

    def effect(self, entity):
        """
        Causes the entity that equips this have a spoofed component child.
        """
        entity.effect_queue.add(entityeffect.AddSpoofChild(entity, self.spoof_child_factory(), 1))
        if self.status_icon:
            entity.effect_queue.add(entityeffect.StatusIconEntityEffect(entity, self.status_icon, 1))


class LifeStealEffect(EquippedEffect):
    def __init__(self):
        super(LifeStealEffect, self).__init__()

    def effect(self, entity):
        """
        Causes seen entities to heal holder of this effect upon death.
        """
        e = AddEffectToOtherSeenEntities(lambda: HealAnEntityOnDeath(entity))
        entity.effect_queue.add(entityeffect.AddSpoofChild(entity, e, 1))
        entity.effect_queue.add(entityeffect.StatusIconEntityEffect(entity, LIFE_STEAL_STATUS_ICON,
                                                                    1, "life_steal_effect"))


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
    item.set_child(DataPoint(DataTypes.WEIGHT, 4))
    #potion.set_child(Stacker("health_potion", 3))


def new_health_potion(game_state):
    potion = Composite()
    set_item_components(potion, game_state)
    set_potion_components(potion)
    potion.set_child(GraphicChar(None, colors.PINK, icon.POTION))
    potion.set_child(HealthPotionDrinkAction())
    potion.set_child(Description("Potion of Health",
                                 "An unusually thick liquid contained in a glass bottle."
                                 "Drinking from it will heal you."))
    potion.set_child(ThrowerBreakCreateSteam())
    return potion


def new_poison_potion(game_state):
    potion = Composite()
    set_item_components(potion, game_state)
    set_potion_components(potion)
    potion.set_child(GraphicChar(None, colors.GREEN, icon.POTION))
    potion.set_child(PoisonPotionDrinkAction())
    potion.set_child(Description("Potion of Poison",
                                 "An unusually sluggish liquid contained in a glass bottle."
                                 "Drinking from it would poison you."))
    potion.set_child(ThrowerBreakCreatePoisonCloud())
    return potion


def new_flame_potion(game_state):
    potion = Composite()
    set_item_components(potion, game_state)
    set_potion_components(potion)
    potion.set_child(GraphicChar(None, colors.RED, icon.POTION))
    potion.set_child(FlamePotionDrinkAction())
    potion.set_child(Description("Potion of Fire",
                                 "An unusually muddy liquid contained in a glass bottle."
                                 "Drinking from it would burn you badly."))
    potion.set_child(ThrowerBreakCreateFire())
    return potion


def set_scroll_components(item):
    item.set_child(ItemType(ItemType.SCROLL))
    item.set_child(PlayerAutoPickUp())
    item.set_child(DataPoint(DataTypes.WEIGHT, 1))
    item.set_child(GraphicChar(None, colors.CHAMPAGNE, icon.SCROLL))


def new_teleport_scroll(game_state):
    scroll = Composite()
    set_item_components(scroll, game_state)
    set_scroll_components(scroll)
    scroll.set_child(GraphicChar(None, colors.CHAMPAGNE, icon.SCROLL))
    scroll.set_child(TeleportScrollReadAction())
    scroll.set_child(Description("Scroll of Teleport",
                                 "A scroll with strange symbols on."
                                 "When read you will appear in a different position."))
    return scroll


def new_map_scroll(game_state):
    scroll = Composite()
    set_item_components(scroll, game_state)
    set_scroll_components(scroll)
    scroll.set_child(GraphicChar(None, colors.CHAMPAGNE, icon.SCROLL))
    scroll.set_child(MapScrollReadAction())
    scroll.set_child(Description("Scroll of magic mapping.",
                                 "A scroll which will make a map of your surroundings."))
    return scroll

def new_bomb(game_state):
    bomb = Composite()
    set_item_components(bomb, game_state)
    bomb.set_child(ItemType(ItemType.BOMB))
    bomb.set_child(PlayerAutoPickUp())
    bomb.set_child(GraphicChar(None, colors.GRAY_D, icon.BOMB))
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


class UsableOnceItemAction(Action):
    """
    Abstract class, drink actions should inherit from this class.
    """

    def act(self, **kwargs):
        """
        Performs the drink action, subclasses should not override this.
        """
        target_entity = kwargs[action.TARGET_ENTITY]
        source_entity = kwargs[action.SOURCE_ENTITY]
        self._act(target_entity)
        self.remove_from_inventory(target_entity)
        _item_flash_animation(source_entity, self.parent)
        self.add_energy_spent_to_entity(source_entity)

    def remove_from_inventory(self, target_entity):
        """
        Removes the parent item from the inventory.
        """
        target_entity.inventory.remove_one_item_from_stack(self.parent)


class DrinkAction(UsableOnceItemAction):
    """
    Abstract class, drink actions should inherit from this class.
    """

    def __init__(self):
        super(DrinkAction, self).__init__()
        self.name = "Drink"
        self.tags.add("drink_action")
        self.display_order = 90


class ReadAction(UsableOnceItemAction):
    """
    Abstract class, drink actions should inherit from this class.
    """

    def __init__(self):
        super(ReadAction, self).__init__()
        self.name = "Read"
        self.tags.add("read_action")
        self.display_order = 90


class HealthPotionDrinkAction(DrinkAction):
    """
    Defines the healing potion drink action.
    """

    def __init__(self):
        super(HealthPotionDrinkAction, self).__init__()
        self.component_type = "health_potion_drink_action"
        self.min_heal = 10
        self.max_heal = 15

    def _act(self, target_entity):
        """
        When an entity drinks a healing potion, it is healed.
        """
        heal = random.randrange(self.min_heal, self.max_heal + 1)
        heal_effect = entityeffect.Heal(target_entity, heal, heal_message=messenger.HEALTH_POTION_MESSAGE)
        target_entity.effect_queue.add(heal_effect)


class FlamePotionDrinkAction(DrinkAction):
    """
    Defines the healing potion drink action.
    """
    def __init__(self):
        super(FlamePotionDrinkAction, self).__init__()
        self.component_type = "flame_potion_drink_action"
        self.min_fire_time = 3
        self.max_fire_time = 8

    def _act(self, target_entity):
        """
        When an entity drinks a flame potion, surrounding tiles and players tile catch fire.
        """
        put_tile_and_surrounding_tiles_on_fire(target_entity.dungeon_level.value, target_entity.position.value,
                                               self.min_fire_time, self.max_fire_time, target_entity.game_state.value)


class PoisonPotionDrinkAction(DrinkAction):
    """
    Defines the poison potion drink action.
    """
    def __init__(self):
        super(PoisonPotionDrinkAction, self).__init__()
        self.component_type = "poison_potion_drink_action"
        self.min_damage = 10
        self.max_damage = 15

    def _act(self, target_entity):
        """
        When an entity drinks a poison potion, it is poisoned.
        """
        damage = random.randrange(self.min_damage, self.max_damage + 1)
        damage_effect_factory = PoisonEntityEffectFactory(target_entity, damage, 2, random.randrange(8, 12))
        target_entity.effect_queue.add(damage_effect_factory())


class TeleportScrollReadAction(ReadAction):
    """
    Defines the healing potion drink action.
    """

    def __init__(self):
        super(TeleportScrollReadAction, self).__init__()
        self.component_type = "teleport_scroll_read_action"

    def _act(self, target_entity):
        """
        When an entity reads a scroll of teleportation it's teleported.
        """
        msg.send_global_message(messenger.PLAYER_TELEPORT_MESSAGE)
        teleport_effect = entityeffect.Teleport(target_entity)
        target_entity.effect_queue.add(teleport_effect)


class MapScrollReadAction(ReadAction):
    """
    Defines the healing potion drink action.
    """

    def __init__(self):
        super(MapScrollReadAction, self).__init__()
        self.component_type = "map_scroll_read_action"

    def _act(self, target_entity):
        """
        When an entity reads a scroll of mapping it gains knowledge of the surrounding terrain.
        """
        msg.send_global_message(messenger.PLAYER_MAP_MESSAGE)
        dungeon_level = target_entity.dungeon_level.value
        walkable_positions = dungeon_level.get_walkable_positions(dummy_flyer,
                                                                  target_entity.position.value)
        map_positions = extend_points(walkable_positions)
        for p in map_positions:
            tile = dungeon_level.get_tile_or_unknown(p)
            target_entity.memory_map.gain_knowledge_of_terrain_of_tile(tile, p, dungeon_level.depth)
        target_entity.game_state.value.dungeon_needs_redraw = True


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


class AttackProvider(Leaf):
    """
    The modify be us, actual damage will be calculated on use.
    """

    def __init__(self, damage, variance, types):
        super(AttackProvider, self).__init__()
        self.component_type = "attack_provider"
        self.damage = damage
        self.variance = variance
        self.types = types

    def attack_entity(self, source_entity, target_entity, bonus_damage=0, bonus_hit=0):
        damage_strength = self.damage + source_entity.strength.value / 2
        damage = Attack(damage_strength, self.variance,
                        self.types, self.parent.hit.value)

        for effect in self.parent.get_children_with_tag("attack_effect"):
            effect.try_apply_effect(source_entity, target_entity)

        return damage.damage_entity(source_entity, target_entity,
                                    bonus_damage=bonus_damage, bonus_hit=bonus_hit)


class AttackEffect(Leaf):
    def __init__(self, effect_chance):
        super(AttackEffect, self).__init__()
        self.effect_chance = effect_chance
        self.tags.add("attack_effect")

    def try_apply_effect(self, source_entity, target_entity):
        if random.random() < self.effect_chance:
            self._apply_effect(source_entity, target_entity)

    def _apply_effect(self, source_entity, target_entity):
        pass


class StunAttackEffect(AttackEffect):
    def __init__(self, effect_chance):
        super(StunAttackEffect, self).__init__(effect_chance)
        self.effect_chance = effect_chance
        self.component_type = "stun_attack_effect"

    def _apply_effect(self, source_entity, target_entity):
        entity_skip_turn(source_entity, target_entity)


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

    """
    When the floor is a chasm it should not break the chasm will take care of the fall.
    """
    def _non_break(self, dungeon_level, position):
        self.parent.mover.try_move(position, dungeon_level)


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
        self._non_break(dungeon_level, position)
        message = messenger.ITEM_HITS_THE_GROUND % {"target_entity": self.parent.description.name}
        msg.send_visual_message(message, position)


class ThrowerBreak(Thrower):
    """
    Items with this component can be thrown, but will survive the fall.
    """

    def __init__(self):
        super(ThrowerBreak, self).__init__()

    def throw_effect(self, dungeon_level, position):
        if is_hitting_ground(dungeon_level, position):
            self._break_effect(dungeon_level, position)
        else:
            self._non_break(dungeon_level, position)

    def _break_effect(self, dungeon_level, position):
        message = "The " + self.parent.description.name.lower() + \
                  " smashes to the ground and breaks into pieces."
        msg.send_visual_message(message, position)

    def _non_break(self, dungeon_level, position):
        """
        When the floor is a chasm it should not break the chasm will take care of the fall.
        """
        self.parent.mover.try_move(position, dungeon_level)
        message = "The " + self.parent.description.name.lower() + \
                  " hits the ground with a thud."
        msg.send_visual_message(message, position)


def is_hitting_ground(dungeon_level, position):
    return not dungeon_level.get_tile_or_unknown(position).get_terrain().has("is_chasm")


class ThrowerBreakCreateCloud(ThrowerBreak):
    """
    Should be sub-classed to items with this component will create and create a puff of cloud.
    """

    def __init__(self):
        super(ThrowerBreakCreateCloud, self).__init__()
        self.cloud_factory = None

    def _break_effect(self, dungeon_level, position):
        message = messenger.POTION_SMASH_TO_GROUND % {"target_entity": self.parent.description.name}
        msg.send_visual_message(message, position)
        steam = self.cloud_factory(self.parent.game_state.value, 32)
        steam.mover.try_move(position, dungeon_level)


class ThrowerBreakCreateSteam(ThrowerBreakCreateCloud):

    def __init__(self):
        super(ThrowerBreakCreateSteam, self).__init__()
        self.cloud_factory = new_steam_cloud


class ThrowerBreakCreatePoisonCloud(ThrowerBreakCreateCloud):

    def __init__(self):
        super(ThrowerBreakCreatePoisonCloud, self).__init__()
        self.cloud_factory = new_poison_cloud


class ThrowerBreakCreateFire(ThrowerBreakCreateCloud):
    def __init__(self):
        super(ThrowerBreakCreateFire, self).__init__()
        self.min_fire_time = 3
        self.max_fire_time = 8

    def _break_effect(self, dungeon_level, position):
        put_tile_and_surrounding_tiles_on_fire(dungeon_level, position, self.min_fire_time, self.max_fire_time,
                                               self.parent.game_state.value)


def put_tile_and_surrounding_tiles_on_fire(dungeon_level, position, min_fire_time, max_fire_time, game_state):
    fire = new_fire_cloud(game_state, random.randrange(min_fire_time, max_fire_time))
    fire.mover.replace_move(position, dungeon_level)
    for d in direction.DIRECTIONS:
        point = geometry.add_2d(d, position)
        fire = new_fire_cloud(game_state, random.randrange(min_fire_time, max_fire_time))
        fire.mover.replace_move(point, dungeon_level)


class ThrowerCreateExplosion(ThrowerBreak):
    """
    Items with this component will create and create a puff of steam.
    """

    def __init__(self):
        super(ThrowerCreateExplosion, self).__init__()

    def _break_effect(self, dungeon_level, position):
        message = messenger.ENTITY_EXPLODES % {"target_entity": self.parent.description.name}
        msg.send_visual_message(message, position)
        game_state = self.parent.game_state.value
        explosion = new_explosion_cloud(game_state, 1)
        explosion.graphic_char.color_fg = colors.YELLOW
        explosion.mover.replace_move(position, dungeon_level)
        for d in direction.DIRECTIONS:
            if d in direction.AXIS_DIRECTIONS:
                color = colors.ORANGE
            else:
                color = colors.RED
            point = geometry.add_2d(d, position)
            explosion = new_explosion_cloud(game_state, 1)
            explosion.graphic_char.color_fg = color
            explosion.mover.replace_move(point, dungeon_level)


def _item_flash_animation(entity, item):
    entity.char_printer.append_graphic_char_temporary_frames([item.graphic_char])
