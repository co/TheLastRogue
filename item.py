import random

from Status import DAMAGE_REFLECT_STATUS_DESCRIPTION
from action import Action
from actor import DoNothingActor
from cloud import new_explosion_cloud, new_frost_cloud, new_poison_cloud
from compositecore import Leaf, Composite
import direction
import geometry
from graphic import GraphicChar, CharPrinter
from health import ReflectDamageTakenEffect
from item_components import ChargeADeviceAction, DarknessDeviceAction, GlassDeviceAction, \
    SwapDeviceAction, HeartStopDeviceAction, BlinksDeviceAction, HealDeviceAction, ZapDeviceAction, Stacker, \
    AddSpoofChildEquipEffect, HealTriggeredEffect, ApplyPoisonTriggeredEffect, CreateFlameCloudTriggeredEffect, \
    ApplyFrostTriggeredEffect, ReEquipAction, DropItemTriggeredEffect, \
    AddEnergySpentEffect, PutToSleepTriggeredEffect, RemoveItemEffect, FlashItemEffect, LocalMessageEffect, Trigger, \
    TeleportTriggeredEffect, SingleSwapTriggeredEffect, MagicMappingTriggeredEffect, PushOthersTriggeredEffect, \
    EquipmentType, PlayerAutoPickUp, ItemType, _item_flash_animation, CreateCloudTriggeredEffect, MoveTriggeredEffect, \
    ExplodeTriggeredEffect
import messenger
from missileaction import PlayerThrowItemAction
from mover import Mover
from position import Position, DungeonLevel
from stats import DataPoint, Flag, DataTypes, GamePieceTypes
from text import Description
import action
import colors
import equipment
import gametime
from messenger import msg
import icon
from equipmenteffect import StatBonusEquipEffect, LifeStealEffect, SetInvisibilityFlagEquippedEffect


def set_item_components(item, game_state):
    item.set_child(DataPoint(DataTypes.ENERGY, -gametime.single_turn))
    item.set_child(Position())
    item.set_child(DoNothingActor())
    item.set_child(DungeonLevel())
    item.set_child(Mover())
    item.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.ITEM))
    item.set_child(DataPoint(DataTypes.GAME_STATE, game_state))
    item.set_child(CharPrinter())
    new_drop_action(DROP_ACTION_TAG, item)
    item.set_child(PlayerThrowItemAction())
    set_thrown_item_hit_floor_action(item, [MoveTriggeredEffect(), LocalMessageEffect(messenger.ITEM_HITS_THE_GROUND_HEAVY)])
    set_thrown_item_hit_chasm_action(item, [MoveTriggeredEffect(), LocalMessageEffect(messenger.ITEM_FALLS_DOWN_CHASM)])
    return item


def set_device_components(item):
    item.set_child(ItemType(ItemType.DEVICE))
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


def new_zap_device(game_state):
    device = Composite()
    set_item_components(device, game_state)
    set_device_components(device)
    device.set_child(Description("Device of Zapping",
                                 "This ancient device will zap a random creature within view."))
    device.set_child(ZapDeviceAction())
    device.set_child(GraphicChar(None, colors.GRAY, icon.MACHINE))
    return device


def new_healing_device(game_state):
    device = Composite()
    set_item_components(device, game_state)
    set_device_components(device)
    device.set_child(Description("Device of Healing",
                                 "This ancient device will heal everything within view."))
    device.set_child(HealDeviceAction())
    device.set_child(GraphicChar(None, colors.PINK, icon.MACHINE))
    return device


def new_blinks_device(game_state):
    device = Composite()
    set_item_components(device, game_state)
    set_device_components(device)
    device.set_child(Description("Device of Blinks",
                                 "This ancient device will repeatedly teleport all creatuers within view short distances."))
    device.set_child(BlinksDeviceAction())
    device.set_child(GraphicChar(None, colors.PURPLE, icon.MACHINE))
    return device


def new_energy_sphere(game_state):
    """
    A composite component representing a gun ammunition item.
    """
    charge = Composite()
    set_item_components(charge, game_state)
    charge.set_child(ItemType(ItemType.ENERGY_SHPERE))
    charge.set_child(Stacker("charge", 5, random.randrange(1, 3)))
    charge.set_child(Description("Energy Sphere",
                                 "These spheres are used to power ancient devices."))
    charge.set_child(GraphicChar(None, colors.LIGHT_ORANGE, icon.BIG_CENTER_DOT))
    charge.set_child(DataPoint(DataTypes.WEIGHT, 1))
    charge.set_child(PlayerAutoPickUp())
    charge.set_child(ChargeADeviceAction())
    return charge


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


def new_boots_of_running(game_state):
    """
    A composite component representing a Boots Armor item.
    """
    boots = Composite()
    set_item_components(boots, game_state)
    set_armor_components(boots)
    boots.set_child(Description("Boots of Running",
                                "A light pair of boots, they make your movement speed faster."))
    boots.set_child(DataPoint(DataTypes.WEIGHT, 2))
    boots.set_child(GraphicChar(None, colors.GREEN, icon.BOOTS))
    boots.set_child(StatBonusEquipEffect("armor", 0))
    boots.set_child(EquipmentType(equipment.EquipmentTypes.BOOTS))
    boots.set_child(StatBonusEquipEffect(DataTypes.MOVEMENT_SPEED, -gametime.quarter_turn))
    return boots


def new_boots_of_sneaking(game_state):
    """
    A composite component representing a Boots Armor item.
    """
    boots = Composite()
    set_item_components(boots, game_state)
    set_armor_components(boots)
    boots.set_child(Description("Boots of sneaking",
                                "A smooth pair of boots, they make you more stealthy."))
    boots.set_child(DataPoint(DataTypes.WEIGHT, 2))
    boots.set_child(GraphicChar(None, colors.BLUE, icon.BOOTS))
    boots.set_child(StatBonusEquipEffect("armor", 0))
    boots.set_child(StatBonusEquipEffect(DataTypes.STEALTH, 3))
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
                                              DAMAGE_REFLECT_STATUS_DESCRIPTION))
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
    amulet.set_child(Description("Amulet of Vampirism",
                                 "The gem at the center pulsates when blood is near."
                                 "Its magic powers will heal when you see a creature die."))
    return amulet


def set_armor_components(item):
    item.set_child(ItemType(ItemType.ARMOR))
    item.set_child(ReEquipAction())
    return item


def set_potion_components(item):
    item.set_child(ItemType(ItemType.POTION))
    item.set_child(PlayerAutoPickUp())
    item.set_child(DataPoint(DataTypes.WEIGHT, 4))
    # potion.set_child(Stacker("health_potion", 3))


# Potions
def new_health_potion(game_state):
    potion = Composite()
    set_item_components(potion, game_state)
    set_potion_components(potion)
    potion.set_child(GraphicChar(None, colors.PINK, icon.POTION))
    set_drink_item_action(potion, [HealTriggeredEffect(10, 15, messenger.HEALTH_POTION_MESSAGE)])
    potion.set_child(Description("Potion of Health",
                                 "An unusually thick liquid contained in a glass bottle."
                                 "Drinking from it will heal you."))
    set_thrown_item_hit_floor_action(potion, [LocalMessageEffect(messenger.POTION_SMASH_TO_GROUND)])
    return potion


def new_poison_potion(game_state):
    potion = Composite()
    set_item_components(potion, game_state)
    set_potion_components(potion)
    potion.set_child(GraphicChar(None, colors.GREEN, icon.POTION))
    set_drink_item_action(potion, [ApplyPoisonTriggeredEffect(10, 15),
                                   LocalMessageEffect(messenger.POISON_POTION_DRINK_MESSAGE)])
    potion.set_child(Description("Potion of Poison",
                                 "An unusually sluggish liquid contained in a glass bottle."
                                 "Drinking from it would poison you."))
    set_thrown_item_hit_floor_action(potion, [CreateCloudTriggeredEffect(cloud_factory=new_poison_cloud),
                                              LocalMessageEffect(messenger.POISON_POTION_BREAK_MESSAGE)])
    return potion


def new_flame_potion(game_state):
    potion = Composite()
    set_item_components(potion, game_state)
    set_potion_components(potion)
    potion.set_child(GraphicChar(None, colors.RED, icon.POTION))
    set_drink_item_action(potion, [CreateFlameCloudTriggeredEffect(),
                                   LocalMessageEffect(messenger.FLAME_POTION_DRINK_MESSAGE)])
    potion.set_child(Description("Potion of Fire",
                                 "An unusually muddy liquid contained in a glass bottle."
                                 "Drinking from it would burn you badly."))
    set_thrown_item_hit_floor_action(potion, [CreateFlameCloudTriggeredEffect(),
                                              LocalMessageEffect(messenger.FLAME_POTION_BREAKS_MESSAGE)])
    return potion


def new_frost_potion(game_state):
    potion = Composite()
    set_item_components(potion, game_state)
    set_potion_components(potion)
    potion.set_child(GraphicChar(None, colors.BLUE, icon.POTION))
    set_drink_item_action(potion, [ApplyFrostTriggeredEffect()])
    potion.set_child(Description("Potion of Frost",
                                 "A soapy liquid contained in a glass bottle."
                                 "Drinking from it would freeze you badly."))
    set_thrown_item_hit_floor_action(potion, [CreateCloudTriggeredEffect(cloud_factory=new_frost_cloud),
                                              LocalMessageEffect(messenger.FROST_POTION_BREAKS_MESSAGE)])
    return potion


def set_drink_item_action(item, triggered_effects):
    set_use_item_action(DRINK_ACTION_TAG, item, [action.TriggerAction("Drink", 90, [DRINK_ACTION_TAG])] + triggered_effects)


def set_thrown_item_hit_floor_action(item, triggered_effects):
    set_use_item_action(HIT_FLOOR_ACTION_TAG, item, [Trigger([HIT_FLOOR_ACTION_TAG])] + triggered_effects)


def set_thrown_item_hit_chasm_action(item, triggered_effects):
    set_use_item_action(HIT_CHASM_ACTION_TAG, item, [Trigger([HIT_CHASM_ACTION_TAG])] + triggered_effects)


potion_factories = [new_health_potion, new_poison_potion, new_flame_potion, new_frost_potion]


# Scrolls
def set_scroll_components(item):
    item.set_child(ItemType(ItemType.SCROLL))
    item.set_child(PlayerAutoPickUp())
    item.set_child(DataPoint(DataTypes.WEIGHT, 1))
    item.set_child(GraphicChar(None, colors.CHAMPAGNE, icon.SCROLL))
    set_thrown_item_hit_floor_action(item, [MoveTriggeredEffect(), LocalMessageEffect(messenger.ITEM_HITS_THE_GROUND_LIGHT)])


def new_teleport_scroll(game_state):
    scroll = Composite()
    set_item_components(scroll, game_state)
    set_scroll_components(scroll)
    set_read_item_action(scroll, [TeleportTriggeredEffect()])
    scroll.set_child(Description("Scroll of Teleport",
                                 "A scroll with strange symbols on."
                                 "When read you will appear in a different position."))
    return scroll


def new_swap_scroll(game_state):
    scroll = Composite()
    set_item_components(scroll, game_state)
    set_scroll_components(scroll)
    set_read_item_action(scroll, [SingleSwapTriggeredEffect()])
    scroll.set_child(Description("Scroll of Swap",
                                 "A scroll with strange symbols on"
                                 "When read you will swap position with another creature on the same floor."))
    return scroll


def new_push_scroll(game_state):
    scroll = Composite()
    set_item_components(scroll, game_state)
    set_scroll_components(scroll)
    set_read_item_action(scroll, [PushOthersTriggeredEffect()])
    scroll.set_child(Description("Scroll of Pushing",
                                 "A scroll which will push all seen creatures away from you."))
    return scroll


def new_map_scroll(game_state):
    scroll = Composite()
    set_item_components(scroll, game_state)
    set_scroll_components(scroll)
    set_read_item_action(scroll, [MagicMappingTriggeredEffect()])
    scroll.set_child(Description("Scroll of Magic Mapping",
                                 "A scroll which will make a map of your surroundings."))
    return scroll


def new_sleep_scroll(game_state):
    scroll = Composite()
    set_item_components(scroll, game_state)
    set_scroll_components(scroll)
    scroll.remove_component_of_type("player_throw_item_action")

    set_read_item_action(scroll, [PutToSleepTriggeredEffect()])
    scroll.set_child(Description("Scroll of Sleep",
                                 "A scroll which will put all seen creatures to sleep."))
    return scroll


def set_read_item_action(item, triggered_effects):
    set_use_item_action(READ_ACTION_TAG, item, [action.TriggerAction("Read", 90, [READ_ACTION_TAG, USER_ACTION_TAG])] + triggered_effects)


scroll_factories = [new_sleep_scroll, new_map_scroll, new_teleport_scroll, new_swap_scroll]


def set_use_item_action(component_type, item, triggered_effects):
    item_trigger_effect = Composite(component_type)
    item_trigger_effect.set_child(FlashItemEffect())  # todo: does this do anything?
    item_trigger_effect.set_child(RemoveItemEffect())
    item_trigger_effect.set_child(AddEnergySpentEffect())
    for triggered_effect in triggered_effects:
        item_trigger_effect.set_child(triggered_effect)
    item_trigger_effect.set_child(DataPoint("item", item))
    item.set_child(item_trigger_effect)


def new_drop_action(component_type, item):
    effect = Composite(component_type)
    effect.set_child(DropItemTriggeredEffect())
    effect.set_child(DataPoint("item", item))
    effect.set_child(action.TriggerAction("Drop", 110, [DROP_ACTION_TAG, USER_ACTION_TAG]))
    item.set_child(effect)


def new_throw_item_action(component_type, item):
    effect = Composite(component_type)
    effect.set_child(DropItemTriggeredEffect())
    effect.set_child(DataPoint("item", item))
    effect.set_child(action.TriggerAction("Throw", 110, [THROW_ACTION_TAG, USER_ACTION_TAG]))
    item.set_child(effect)


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
    set_thrown_item_hit_floor_action(bomb, [ExplodeTriggeredEffect(),
                                            LocalMessageEffect(messenger.ENTITY_EXPLODES)])
    return bomb


#TODO to be removed
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


USER_ACTION_TAG = "user_action" # An element with this tag will be visible in menus.
READ_ACTION_TAG = "read_action"
DRINK_ACTION_TAG = "drink_action"
DROP_ACTION_TAG = "drop_action"
THROW_ACTION_TAG = "throw_action"
HIT_FLOOR_ACTION_TAG = "hit_floor_action_tag"
HIT_CHASM_ACTION_TAG = "hit_chasm_action_tag"
