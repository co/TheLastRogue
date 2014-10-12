import action
from attacker import DamageType, DamageTypes, WeaponMeleeAttacker, WeaponRangedAttacker
import colors
from compositecore import Composite, Leaf
import equipment
from equipmenteffect import CritChanceBonusEffect, ExtraSwingAttackEffect, BleedAttackEffect, DefenciveAttackEffect, CounterAttackEffect, StunAttackEffect, IgnoreArmorAttackEffect, RangeItemStat, ItemStat, OffenciveAttackEffect, KnockBackAttackEffect, TripAttackEffect
from graphic import GraphicChar
import icon
from item import EquipmentType, ItemType, AddSpoofChildEquipEffect2, ReEquipAction, set_item_components
from missileaction import PlayerCastMissileSpellAction
from stats import DataPoint, DataTypes, Damage
from text import Description

__author__ = 'co'



def set_melee_weapon_component(item):
    item.set_child(EquipmentType(equipment.EquipmentTypes.MELEE_WEAPON))
    item.set_child(ItemType(ItemType.WEAPON))
    item.set_child(DamageType(DamageTypes.PHYSICAL))
    item.set_child(AddSpoofChildEquipEffect2(WeaponMeleeAttacker(item)))
    item.set_child(ReEquipAction())


def new_dagger(game_state):
    """
    A composite component representing a Knife item.
    """
    c = Composite()
    set_item_components(c, game_state)
    set_melee_weapon_component(c)
    c.set_child(Description("Dagger", "A trusty dagger, small and precise but will only inflict small wounds."))
    c.set_child(GraphicChar(None, colors.GRAY, icon.DAGGER))
    c.set_child(DataPoint(DataTypes.WEIGHT, 5))
    c.set_child(DamageType(DamageTypes.CUTTING))

    c.set_child(damage_item_stat(1, 3))
    c.set_child(accuracy_item_stat(15))

    c.set_child(CritChanceBonusEffect(0.2))
    c.set_child(crit_multiplier_item_stat(3.5))

    c.set_child(ExtraSwingAttackEffect(0.20))
    c.set_child(BleedAttackEffect(0.10))

    return c


def new_kris(game_state):
    """
    A composite component representing a Knife item.
    """
    c = Composite()
    set_item_components(c, game_state)
    set_melee_weapon_component(c)
    c.set_child(Description("Kris", "A dagger with a wavy blade, its sharp end can cause major damage."))
    c.set_child(GraphicChar(None, colors.GRAY_D, icon.KRIS))
    c.set_child(DataPoint(DataTypes.WEIGHT, 5))
    c.set_child(DamageType(DamageTypes.CUTTING))

    c.set_child(damage_item_stat(1, 3))
    c.set_child(accuracy_item_stat(15))

    c.set_child(CritChanceBonusEffect(0.20))
    c.set_child(crit_multiplier_item_stat(3.5))

    c.set_child(ExtraSwingAttackEffect(0.2))
    c.set_child(BleedAttackEffect(0.2))

    return c


def new_katar(game_state):
    """
    A composite component representing a Knife item.
    """
    c = Composite()
    set_item_components(c, game_state)
    set_melee_weapon_component(c)
    c.set_child(Description("Katar", "A blade with an unusual handle, it looks ancient."))
    c.set_child(GraphicChar(None, colors.CHAMPAGNE, icon.KATAR))
    c.set_child(DataPoint(DataTypes.WEIGHT, 5))
    c.set_child(DamageType(DamageTypes.CUTTING))

    c.set_child(damage_item_stat(1, 3))
    c.set_child(accuracy_item_stat(17))

    c.set_child(CritChanceBonusEffect(0.10))
    c.set_child(crit_multiplier_item_stat(3))

    c.set_child(ExtraSwingAttackEffect(0.2))
    c.set_child(CounterAttackEffect(0.2))

    return c


def new_cestus(game_state):
    c = Composite()
    set_item_components(c, game_state)
    set_melee_weapon_component(c)
    c.set_child(Description("Cestus", "A pair of leather battle gloves, they improve your punches."))
    c.set_child(GraphicChar(None, colors.ORANGE_D, icon.GLOVE))
    c.set_child(DataPoint(DataTypes.WEIGHT, 5))
    c.set_child(DamageType(DamageTypes.BLUNT))

    c.set_child(damage_item_stat(1, 3))
    c.set_child(accuracy_item_stat(17))

    c.set_child(CritChanceBonusEffect(0.10))
    c.set_child(crit_multiplier_item_stat(2))

    c.set_child(ExtraSwingAttackEffect(0.3))
    c.set_child(CounterAttackEffect(0.2))
    c.set_child(StunAttackEffect(0.2))

    return c


def new_iron_hand(game_state):
    c = Composite()
    set_item_components(c, game_state)
    set_melee_weapon_component(c)
    c.set_child(Description("Iron Hand", "A pair of iron battle gloves, they put weight into your punches."))
    c.set_child(GraphicChar(None, colors.GRAY, icon.GLOVE))
    c.set_child(DataPoint(DataTypes.WEIGHT, 5))
    c.set_child(DamageType(DamageTypes.BLUNT))

    c.set_child(damage_item_stat(1, 3))
    c.set_child(accuracy_item_stat(14))

    c.set_child(CritChanceBonusEffect(0.10))
    c.set_child(crit_multiplier_item_stat(2))

    c.set_child(ExtraSwingAttackEffect(0.20))
    c.set_child(CounterAttackEffect(0.2))
    c.set_child(StunAttackEffect(0.35))

    return c


def new_claw(game_state):
    c = Composite()
    set_item_components(c, game_state)
    set_melee_weapon_component(c)
    c.set_child(Description("Claws", "A pair of gloves with sharp blades attached to them,"))
    c.set_child(GraphicChar(None, colors.CHAMPAGNE, icon.CLAWS))
    c.set_child(DataPoint(DataTypes.WEIGHT, 5))
    c.set_child(DamageType(DamageTypes.BLUNT))

    c.set_child(damage_item_stat(1, 3))
    c.set_child(accuracy_item_stat(17))

    c.set_child(CritChanceBonusEffect(0.10))
    c.set_child(crit_multiplier_item_stat(2))

    c.set_child(ExtraSwingAttackEffect(0.15))
    c.set_child(CounterAttackEffect(0.20))
    c.set_child(BleedAttackEffect(0.30))

    return c


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
    sword.set_child(DataPoint(DataTypes.WEIGHT, 10))

    sword.set_child(damage_item_stat(2, 5))
    sword.set_child(accuracy_item_stat(10))

    sword.set_child(crit_chance_item_stat(0.1))
    sword.set_child(crit_multiplier_item_stat(2))

    sword.set_child(ExtraSwingAttackEffect(0.1))
    sword.set_child(BleedAttackEffect(0.1))
    return sword


def new_rapier(game_state):
    """
    A composite component representing a Sword item.
    """
    sword = Composite()
    set_item_components(sword, game_state)
    set_melee_weapon_component(sword)
    sword.set_child(Description("Rapier",
                                "A sword with a thin sharp blade, swift but deadly."))
    sword.set_child(GraphicChar(None, colors.CHAMPAGNE, icon.RAPIER))
    sword.set_child(DataPoint(DataTypes.WEIGHT, 8))

    sword.set_child(damage_item_stat(2, 5))
    sword.set_child(accuracy_item_stat(10))

    sword.set_child(crit_chance_item_stat(0.2))
    sword.set_child(crit_multiplier_item_stat(2.5))

    sword.set_child(ExtraSwingAttackEffect(0.1))
    sword.set_child(CounterAttackEffect(0.1))
    sword.set_child(OffenciveAttackEffect(0.1))
    return sword


def new_scimitar(game_state):
    """
    A composite component representing a Sword item.
    """
    sword = Composite()
    set_item_components(sword, game_state)
    set_melee_weapon_component(sword)
    sword.set_child(Description("Scimitar",
                                "A curved sword, an ancient design from the east."))
    sword.set_child(GraphicChar(None, colors.WHITE, icon.SCIMITAR))
    sword.set_child(DataPoint(DataTypes.WEIGHT, 8))

    sword.set_child(damage_item_stat(2, 5))
    sword.set_child(accuracy_item_stat(12))

    sword.set_child(crit_chance_item_stat(0.2))
    sword.set_child(crit_multiplier_item_stat(2.5))

    sword.set_child(ExtraSwingAttackEffect(0.1))
    sword.set_child(DefenciveAttackEffect(0.1))
    sword.set_child(OffenciveAttackEffect(0.1))
    return sword


def new_club(game_state):
    """
    A composite component representing a Sword item.
    """
    c = Composite()
    set_item_components(c, game_state)
    set_melee_weapon_component(c)
    c.set_child(Description("Club",
                                "A thick wooden stick, It may be used as a weapon."))
    c.set_child(GraphicChar(None, colors.ORANGE_D, icon.CLUB))
    c.set_child(DataPoint(DataTypes.WEIGHT, 8))

    c.set_child(damage_item_stat(1, 6))
    c.set_child(accuracy_item_stat(8))

    c.set_child(crit_chance_item_stat(0.1))
    c.set_child(crit_multiplier_item_stat(1.5))

    c.set_child(StunAttackEffect(0.3))
    return c


def new_morning_star(game_state):
    """
    A composite component representing a Sword item.
    """
    mace = Composite()
    set_item_components(mace, game_state)
    set_melee_weapon_component(mace)
    mace.set_child(Description("Morning Star",
                               "This old club has an lump of iron with rusty spikes at one end."))
    mace.set_child(GraphicChar(None, colors.GRAY, icon.MORNING_STAR))
    mace.set_child(DataPoint(DataTypes.WEIGHT, 8))

    mace.set_child(accuracy_item_stat(8))
    mace.set_child(damage_item_stat(1, 6))

    mace.set_child(crit_chance_item_stat(0.1))
    mace.set_child(crit_multiplier_item_stat(2))

    mace.set_child(StunAttackEffect(0.2))
    mace.set_child(IgnoreArmorAttackEffect(0.2))
    mace.set_child(BleedAttackEffect(0.1))

    return mace


def new_flail(game_state):
    """
    A composite component representing a Sword item.
    """
    c = Composite()
    set_item_components(c, game_state)
    set_melee_weapon_component(c)
    c.set_child(Description("Flail",
                            "A wooden handle with a chain and metal ball attached to it."))
    c.set_child(GraphicChar(None, colors.GRAY, icon.FLAIL))
    c.set_child(DataPoint(DataTypes.WEIGHT, 8))

    c.set_child(damage_item_stat(1, 7))
    c.set_child(accuracy_item_stat(7))

    c.set_child(crit_chance_item_stat(0.15))
    c.set_child(crit_multiplier_item_stat(2))

    c.set_child(IgnoreArmorAttackEffect(0.3))
    c.set_child(KnockBackAttackEffect(0.2))
    c.set_child(OffenciveAttackEffect(0.1))
    return c


def new_hammer(game_state):
    """
    A composite component representing a Sword item.
    """
    c = Composite()
    set_item_components(c, game_state)
    set_melee_weapon_component(c)
    c.set_child(Description("Hammer",
                            "A heavy hammer, it may knock away enemies."))
    c.set_child(GraphicChar(None, colors.GRAY, icon.HAMMER))
    c.set_child(DataPoint(DataTypes.WEIGHT, 8))

    c.set_child(damage_item_stat(1, 7))
    c.set_child(accuracy_item_stat(8))

    c.set_child(crit_chance_item_stat(0.15))
    c.set_child(crit_multiplier_item_stat(2))

    c.set_child(KnockBackAttackEffect(0.35))
    return c


def new_chain_and_ball(game_state):
    """
    A composite component representing a Sword item.
    """
    c = Composite()
    set_item_components(c, game_state)
    set_melee_weapon_component(c)
    c.set_child(Description("Chain and Spike Ball",
                            "A huge metal ball on a chain, hard to use but can deal massive damage."))
    c.set_child(GraphicChar(None, colors.GRAY, icon.BALL_AND_CHAIN))
    c.set_child(DataPoint(DataTypes.WEIGHT, 8))

    c.set_child(damage_item_stat(2, 9))
    c.set_child(accuracy_item_stat(5))

    c.set_child(crit_chance_item_stat(0.10))
    c.set_child(crit_multiplier_item_stat(2))

    c.set_child(KnockBackAttackEffect(0.20))
    c.set_child(DefenciveAttackEffect(0.60))
    c.set_child(IgnoreArmorAttackEffect(0.10))
    return c


def new_spear(game_state):
    """
    A composite component representing a Sword item.
    """
    c = Composite()
    set_item_components(c, game_state)
    set_melee_weapon_component(c)
    c.set_child(Description("Spear",
                            "A stick with a sharp piece of metal at one end."
                            "It's a useful weapon when you want to keep danger at bay."))
    c.set_child(GraphicChar(None, colors.GRAY, icon.SPEAR))
    c.set_child(DataPoint(DataTypes.WEIGHT, 8))

    c.set_child(accuracy_item_stat(10))
    c.set_child(damage_item_stat(1, 5))

    c.set_child(crit_chance_item_stat(0.1))
    c.set_child(crit_multiplier_item_stat(2))

    c.set_child(DefenciveAttackEffect(0.75))
    c.set_child(CounterAttackEffect(0.1))

    return c


def new_halberd(game_state):
    """
    A composite component representing a Sword item.
    """
    c = Composite()
    set_item_components(c, game_state)
    set_melee_weapon_component(c)
    c.set_child(Description("Halberd",
                            "A long stick with a with an axe-head at one end."
                            "It's a useful weapon when you want to keep danger at bay."))
    c.set_child(GraphicChar(None, colors.GRAY, icon.HALBERD))
    c.set_child(DataPoint(DataTypes.WEIGHT, 8))

    c.set_child(accuracy_item_stat(10))
    c.set_child(damage_item_stat(1, 5))

    c.set_child(crit_chance_item_stat(0.1))
    c.set_child(crit_multiplier_item_stat(2))

    c.set_child(DefenciveAttackEffect(0.75))
    c.set_child(OffenciveAttackEffect(0.20))

    return c


def new_trident(game_state):
    """
    A composite component representing a Sword item.
    """
    c = Composite()
    set_item_components(c, game_state)
    set_melee_weapon_component(c)
    c.set_child(Description("Trident",
                            "A long stick with a with three sharp points at one end."
                            "It's a useful weapon when you want to keep danger at bay."))
    c.set_child(GraphicChar(None, colors.ORANGE_D, icon.TRIDENT))
    c.set_child(DataPoint(DataTypes.WEIGHT, 8))

    c.set_child(accuracy_item_stat(10))
    c.set_child(damage_item_stat(1, 5))

    c.set_child(crit_chance_item_stat(0.15))
    c.set_child(crit_multiplier_item_stat(2.5))

    c.set_child(DefenciveAttackEffect(0.75))
    c.set_child(BleedAttackEffect(0.20))

    return c


def new_whip(game_state):
    """
    A composite component representing a Sword item.
    """
    c = Composite()
    set_item_components(c, game_state)
    set_melee_weapon_component(c)
    c.set_child(Description("Whip",
                            "An unusual weapon, most often used for torture."))
    c.set_child(GraphicChar(None, colors.ORANGE_D, icon.WHIP))
    c.set_child(DataPoint(DataTypes.WEIGHT, 8))

    c.set_child(accuracy_item_stat(10))
    c.set_child(damage_item_stat(1, 4))

    c.set_child(crit_chance_item_stat(0.15))
    c.set_child(crit_multiplier_item_stat(2.5))

    c.set_child(TripAttackEffect(0.50))
    c.set_child(DefenciveAttackEffect(0.30))
    c.set_child(StunAttackEffect(0.10))

    return c


def new_axe(game_state):
    """
    A composite component representing a Sword item.
    """
    c = Composite()
    set_item_components(c, game_state)
    set_melee_weapon_component(c)
    c.set_child(Description("Axe",
                                "This old axe has seen many battles, but age hasn't dulled the blade."))
    c.set_child(GraphicChar(None, colors.GRAY, icon.AXE))
    c.set_child(DataPoint(DataTypes.WEIGHT, 10))

    c.set_child(damage_item_stat(3, 5))
    c.set_child(accuracy_item_stat(8))

    c.set_child(crit_chance_item_stat(0.1))
    c.set_child(crit_multiplier_item_stat(2))

    c.set_child(OffenciveAttackEffect(0.75))
    c.set_child(BleedAttackEffect(0.1))
    return c


def damage_item_stat(min_value, max_value):
    return RangeItemStat(DataTypes.DAMAGE, min_value, max_value, colors.WHITE, "Damage", order=0)


def accuracy_item_stat(value):
    return ItemStat(DataTypes.ACCURACY, value, colors.LIGHT_ORANGE, "Accuracy", order=10)


def crit_chance_item_stat(value):
    return ItemStat(DataTypes.CRIT_CHANCE, value, colors.RED, "Crit %", ItemStat.PERCENT_FORMAT, order=20)


def crit_multiplier_item_stat(value):
    return ItemStat(DataTypes.CRIT_MULTIPLIER, value, colors.RED, "Crit x", ItemStat.MULTIPLIER_FORMAT, order=30)


def set_ranged_weapon_components(item):
    item.set_child(EquipmentType(equipment.EquipmentTypes.RANGED_WEAPON))
    item.set_child(ItemType(ItemType.WEAPON))
    item.set_child(ReEquipAction())
    item.set_child(AddSpoofChildEquipEffect2(WeaponRangedAttacker(item)))


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
    gun.set_child(DataPoint(DataTypes.WEAPON_RANGE, 15))
    gun.set_child(accuracy_item_stat(13))
    gun.set_child(damage_item_stat(5, 25))
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
    sling.set_child(DataPoint(DataTypes.WEIGHT, 3))
    sling.set_child(accuracy_item_stat(5))
    sling.set_child(Damage(1, 3))
    return sling


def new_flame_orb(game_state):
    orb = Composite()
    set_item_components(orb, game_state)
    set_ranged_weapon_components(orb)
    orb.set_child(RangeWeaponType(RangeWeaponType.MAGIC))
    orb.set_child(Description("Flame Orb",
                              "An orb with a living flame inside, it allows the wielder to channel fire from it."))
    orb.set_child(GraphicChar(None, colors.RED, icon.ORB))
    orb.set_child(DataPoint(DataTypes.WEAPON_RANGE, 5))
    orb.set_child(DataPoint(DataTypes.WEIGHT, 2))
    orb.set_child(accuracy_item_stat(5))
    orb.set_child(Damage(2, 4))
    orb.set_child(MagicMissileEffect(GraphicChar(None, colors.RED, icon.BIG_CENTER_DOT)))
    return orb


class MagicEffect(Leaf):
    def __init__(self):
        super(MagicEffect, self).__init__()
        self.component_type = "magic_effect"

    def cast_magic(self):
        pass


class MagicMissileEffect(MagicEffect):
    def __init__(self, missile_graphic):
        super(MagicMissileEffect, self).__init__()
        self.missile_graphic = missile_graphic

    def cast_magic(self, **kwargs):
        source_entity = kwargs[action.SOURCE_ENTITY]
        casting = PlayerCastMissileSpellAction(self.parent, self.missile_graphic)
        game_state = self.parent.game_state.value
        if casting.can_act(source_entity=source_entity, game_state=game_state):
            casting.act(source_entity=source_entity, game_state=game_state)


class RangeWeaponType(DataPoint):
    """
    Component that marks a weapon as a ranged weapon.
    """

    GUN = 0
    SLING = 1
    MAGIC = 2

    def __init__(self, range_weapon_type):
        super(RangeWeaponType, self).__init__("range_weapon_type", range_weapon_type)