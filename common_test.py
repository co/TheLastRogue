from actor import DoNothingActor
from compositecore import Composite
import dungeonlevelfactory
from equipment import Equipment
from gamestate import GameState, GameStateDummy
import gametime
from graphic import CharPrinter
from inventory import Inventory
from player import Player
from position import DungeonLevel, Position
from stats import DataPoint, DataTypes
from vision import Vision

__author__ = 'co'


dungeon1 = ["#####",
            "#...#",
            "#.#.#",
            "#...#",
            "#####"]
dungeon_level = \
    dungeonlevelfactory.dungeon_level_from_lines(dungeon1)

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
    game_state_dummy = GameStateDummy()
    dummy_actor = game_state_dummy.player
    dummy_actor.dungeon_level.value = dungeon_level
    dummy_actor.set_child(Position())
    dummy_actor.position.value = (1, 1)
    return dummy_actor
