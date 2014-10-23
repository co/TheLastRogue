from pygame.tests.test_utils import unittest

from actionscheduler import ActionScheduler
from actor import DoNothingActor
from compositecore import Composite
from equipment import Equipment
import equipment
from equipmenteffect import CounterAttackEffect, COUNTER_ITEM_STAT_TYPE
import gametime
from item import EquipmentType
from stats import DataPoint, DataTypes


def get_dummy_weapon():
    weapon = Composite()
    weapon.set_child(EquipmentType(equipment.EquipmentTypes.MELEE_WEAPON))
    return weapon


def get_dummy_actor():
    dummy_actor = Composite()
    dummy_actor.set_child(DoNothingActor())
    dummy_actor.set_child(Equipment())
    dummy_actor.set_child(DataPoint(DataTypes.ENERGY, -gametime.single_turn))
    return dummy_actor


class TestComposition(unittest.TestCase):
    def setUp(self):
        self.scheduler = ActionScheduler()
        self.dummy_actor = get_dummy_actor()
        self.scheduler.register(self.dummy_actor)

    def test_weapon_with_counter_attack_effect_gives_weilder_counter_attack_bonus(self):
        test_weapon = get_dummy_weapon()
        bonus = 0.5
        test_weapon.set_child(CounterAttackEffect(bonus))
        self.dummy_actor.set_child(DataPoint(DataTypes.COUNTER_ATTACK_CHANCE, 0.0))
        self.scheduler.register(test_weapon)
        self.assertTrue(self.dummy_actor.equipment.try_equip(test_weapon), "Could not equip weapon")
        self.scheduler.tick()
        self.assertTrue(self.dummy_actor.has(DataTypes.COUNTER_ATTACK_CHANCE), "The actor has no counter bonus stat.")
        self.assertEqual(self.dummy_actor.get_child(DataTypes.COUNTER_ATTACK_CHANCE).value, bonus)
