import unittest

from actionscheduler import ActionScheduler
from attacker import WeaponMeleeAttacker
from common_test import get_dummy_actor
from compositecore import Composite
import equipment
from equipmenteffect import CounterAttackEffect, OffenciveAttackEffect, DefenciveAttackEffect, CritChanceBonusEffect
from item import EquipmentType
from stats import DataTypes

TEST_VALUE = 0.4711


def get_dummy_weapon():
    weapon = Composite()
    weapon.set_child(EquipmentType(equipment.EquipmentTypes.MELEE_WEAPON))
    return weapon


class TestComposition(unittest.TestCase):
    def setUp(self):
        pass

    def weapon_with_player_stat_bonus_should_give_player_stat_bonus(self, bonus_type, expected_bonus, test_weapon, actor):
        scheduler = ActionScheduler()
        scheduler.register(actor)

        self.assertTrue(actor.equipment.try_equip(test_weapon), "Could not equip weapon")
        scheduler.tick()
        self.assertTrue(actor.has(bonus_type), "The actor has no '" + bonus_type + "' bonus stat.")
        self.assertEqual(actor.get_child(bonus_type).value, expected_bonus)

    def test_weapon_with_counter_attack_effect_gives_wielder_counter_attack_bonus(self):
        test_weapon = get_dummy_weapon()
        test_weapon.set_child(CounterAttackEffect(TEST_VALUE))
        self.weapon_with_player_stat_bonus_should_give_player_stat_bonus(DataTypes.COUNTER_ATTACK_CHANCE, TEST_VALUE,
                                                                         test_weapon, get_dummy_actor())

    def test_weapon_with_offencive_attack_effect_gives_wielder_counter_attack_bonus(self):
        test_weapon = get_dummy_weapon()
        test_weapon.set_child(OffenciveAttackEffect(TEST_VALUE))
        self.weapon_with_player_stat_bonus_should_give_player_stat_bonus(DataTypes.OFFENCIVE_ATTACK_CHANCE, TEST_VALUE,
                                                                         test_weapon, get_dummy_actor())

    def test_weapon_with_defencive_attack_effect_gives_wielder_counter_attack_bonus(self):
        test_weapon = get_dummy_weapon()
        test_weapon.set_child(DefenciveAttackEffect(TEST_VALUE))
        self.weapon_with_player_stat_bonus_should_give_player_stat_bonus(DataTypes.DEFENCIVE_ATTACK_CHANCE, TEST_VALUE,
                                                                         test_weapon, get_dummy_actor())

    def test_weapon_with_defencive_attack_effect_gives_wielder_counter_attack_bonus(self):
        test_weapon = get_dummy_weapon()
        test_weapon.set_child(CritChanceBonusEffect(TEST_VALUE))
        actor = get_dummy_actor()
        actor.set_child(WeaponMeleeAttacker(test_weapon))
        self.weapon_with_player_stat_bonus_should_give_player_stat_bonus(DataTypes.CRIT_CHANCE, TEST_VALUE,
                                                                         test_weapon, actor)
        self.assertEqual(actor.melee_attacker.crit_chance, TEST_VALUE)
