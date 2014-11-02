from actor import DoNothingActor
from compositecore import Composite
from equipment import Equipment
import gametime
from graphic import CharPrinter
from inventory import Inventory
from position import DungeonLevel
from stats import DataPoint, DataTypes
from vision import Vision

__author__ = 'co'


def get_dummy_actor():
    dummy_actor = Composite()
    dummy_actor.set_child(DoNothingActor())
    dummy_actor.set_child(Equipment())
    dummy_actor.set_child(DataPoint(DataTypes.ENERGY, -gametime.single_turn))
    dummy_actor.set_child(DataPoint(DataTypes.OFFENCIVE_ATTACK_CHANCE, 0.0))
    dummy_actor.set_child(DataPoint(DataTypes.COUNTER_ATTACK_CHANCE, 0.0))
    dummy_actor.set_child(DataPoint(DataTypes.DEFENCIVE_ATTACK_CHANCE, 0.0))
    dummy_actor.set_child(DataPoint(DataTypes.CRIT_CHANCE, 0.0))

    return dummy_actor


def get_dummy_player():
    dummy_actor = get_dummy_actor()
    dummy_actor.set_child(Inventory())
    dummy_actor.set_child(CharPrinter())
    dummy_actor.set_child(Vision())
    dummy_actor.set_child(DungeonLevel())
    return dummy_actor
