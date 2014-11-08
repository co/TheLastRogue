from Status import StatusDescriptionBar
import constants
from equipment import Equipment
from attacker import Dodger, ArmorChecker, ResistanceChecker, CounterAttackOnDamageTakenEffect, AttackEnemyIStepNextToEffect, AttackEnemySteppingNextToMeEffect, UnarmedAttacker, ThrowRockAttacker
from compositecore import Composite
from dungeonmask import DungeonMask, Path
from entityeffect import EffectQueue
from graphic import CharPrinter, GraphicChar
from health import Health, HealthModifier, BleedWhenDamaged, LoseParalyzeWhenDamaged
from inputactor import InputActor
from inventory import Inventory
from item_components import PickUpItemAction
from memorymap import MemoryMap
from missileaction import PlayerThrowStoneAction
from mover import Mover, PlayerStepper
from ondeath import LeaveCorpseOnDeath
from position import Position, DungeonLevel
from stats import GamePieceTypes, Flag, DataPoint, DataTypes, Factions, IntelligenceLevel, Races, Class

from statusflags import StatusFlags
from text import Description
from vision import Vision, AwarenessChecker
import colors
import gametime
import icon


def new_player(game_state):
    """
    A composite component representing the player character.
    """
    player = Composite()
    player.set_child(DataPoint(DataTypes.GAME_STATE, game_state))

    player.set_child(DataPoint(DataTypes.RACE, Races.HUMAN))

    player.set_child(DataPoint(DataTypes.ENERGY, -gametime.single_turn))
    player.set_child(DataPoint(DataTypes.UNARMED_CRIT_CHANCE, 0.15))
    player.set_child(DataPoint(DataTypes.CRIT_CHANCE, 0.0))
    player.set_child(DataPoint(DataTypes.ACCURACY, 10))
    player.set_child(DataPoint(DataTypes.STRENGTH, 5))
    player.set_child(DataPoint(DataTypes.EVASION, 10))
    player.set_child(DataPoint(DataTypes.ARMOR, 4))
    player.set_child(DataPoint(DataTypes.STEALTH, 6))

    player.set_child(DataPoint(DataTypes.COUNTER_ATTACK_CHANCE, 0.0))
    player.set_child(DataPoint(DataTypes.DEFENCIVE_ATTACK_CHANCE, 0.0))
    player.set_child(DataPoint(DataTypes.OFFENCIVE_ATTACK_CHANCE, 0.0))

    player.set_child(Flag("is_player"))
    player.set_child(Flag("is_named"))
    player.set_child(StatusFlags([StatusFlags.CAN_OPEN_DOORS, StatusFlags.IS_ALIVE]))

    player.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.ENTITY))

    player.set_child(DataPoint(DataTypes.MOVEMENT_SPEED, gametime.single_turn))
    player.set_child(DataPoint(DataTypes.MELEE_SPEED, gametime.single_turn))
    player.set_child(DataPoint(DataTypes.THROW_SPEED, gametime.double_turn))
    player.set_child(DataPoint(DataTypes.SHOOT_SPEED, gametime.single_turn))
    player.set_child(DataPoint(DataTypes.THROW_ITEM_SPEED, gametime.single_turn))
    player.set_child(DataPoint(DataTypes.CAST_SPEED, gametime.single_turn))

    player.set_child(DataPoint(DataTypes.SIGHT_RADIUS, constants.COMMON_SIGHT_RADIUS))
    player.set_child(DataPoint(DataTypes.FACTION, Factions.PLAYER))
    player.set_child(DataPoint(DataTypes.INTELLIGENCE, IntelligenceLevel.NORMAL))

    player.set_child(DungeonLevel())
    player.set_child(Position())

    player.set_child(Mover())
    player.set_child(PlayerStepper())

    player.set_child(UnarmedAttacker())
    player.set_child(ThrowRockAttacker())
    player.set_child(Dodger())
    player.set_child(ArmorChecker())
    player.set_child(ResistanceChecker())

    player.set_child(Description("CO", "The Brave"))
    player.set_child(GraphicChar(None, colors.WHITE, icon.GUNSLINGER_THIN))
    player.set_child(StatusDescriptionBar())
    player.set_child(CharPrinter())

    player.set_child(HealthModifier())
    player.set_child(BleedWhenDamaged())
    player.set_child(LoseParalyzeWhenDamaged())

    player.set_child(CounterAttackOnDamageTakenEffect())
    player.set_child(AttackEnemyIStepNextToEffect())
    player.set_child(AttackEnemySteppingNextToMeEffect())

    player.set_child(PlayerThrowStoneAction())

    player.set_child(DungeonMask())
    player.set_child(Vision())
    player.set_child(AwarenessChecker())

    player.set_child(MemoryMap())
    player.set_child(Inventory())
    player.set_child(InputActor())
    player.set_child(Path())
    player.set_child(Equipment())
    player.set_child(EffectQueue())
    player.set_child(PickUpItemAction())
    player.set_child(LeaveCorpseOnDeath())
    return player
