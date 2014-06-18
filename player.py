from Status import StatusDescriptionBar
import constants
from equipment import Equipment
from item import PickUpItemAction
from attacker import Attacker, Dodger, ArmorChecker, ResistanceChecker
from compositecore import Composite
from dungeonmask import DungeonMask, Path
from entityeffect import EffectQueue
from graphic import CharPrinter, GraphicChar
from health import Health, HealthModifier, BleedWhenDamaged
from inputactor import InputActor
from inventory import Inventory
from memorymap import MemoryMap
from missileaction import PlayerThrowStoneAction
from mover import Mover, Stepper, PlayerStepper
from ondeath import LeaveCorpseOnDeath
from position import Position, DungeonLevel
from stats import GamePieceTypes, Flag, DataPoint, DataTypes, Factions, IntelligenceLevel, Races, Jobs

from statusflags import StatusFlags
from text import Description
from vision import Vision, AwarenessChecker
import colors
import gametime
import icon


class Player(Composite):
    """
    A composite component representing the player character.
    """
    def __init__(self, game_state):
        super(Player, self).__init__()
        self.set_child(Health(25))

        self.set_child(DataPoint(DataTypes.RACE, Races.HUMAN))
        self.set_child(DataPoint(DataTypes.JOB, Jobs.ROGUE))

        self.set_child(DataPoint(DataTypes.ENERGY, -gametime.single_turn))
        self.set_child(DataPoint(DataTypes.CRIT_CHANCE, 0.15))
        self.set_child(DataPoint(DataTypes.STRENGTH, 5))
        self.set_child(DataPoint(DataTypes.EVASION, 15))
        self.set_child(DataPoint(DataTypes.HIT, 16))
        self.set_child(DataPoint(DataTypes.ARMOR, 4))
        self.set_child(DataPoint(DataTypes.STEALTH, 6))

        self.set_child(Flag("is_player"))
        self.set_child(Flag("is_named"))
        self.set_child(StatusFlags([StatusFlags.CAN_OPEN_DOORS, StatusFlags.IS_ALIVE]))

        self.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.ENTITY))
        self.set_child(DataPoint(DataTypes.MOVEMENT_SPEED, gametime.single_turn))
        self.set_child(DataPoint(DataTypes.MELEE_SPEED, gametime.single_turn))
        self.set_child(DataPoint(DataTypes.THROW_SPEED, gametime.double_turn))
        self.set_child(DataPoint(DataTypes.SHOOT_SPEED, gametime.single_turn))
        self.set_child(DataPoint(DataTypes.SIGHT_RADIUS, constants.COMMON_SIGHT_RADIUS))
        self.set_child(DataPoint(DataTypes.FACTION, Factions.PLAYER))
        self.set_child(DataPoint(DataTypes.INTELLIGENCE, IntelligenceLevel.NORMAL))

        self.set_child(DataPoint(DataTypes.GAME_STATE, game_state))

        self.set_child(DungeonLevel())
        self.set_child(Position())

        self.set_child(Mover())
        self.set_child(PlayerStepper())

        self.set_child(Attacker())
        self.set_child(Dodger())
        self.set_child(ArmorChecker())
        self.set_child(ResistanceChecker())

        self.set_child(Description("CO", "The Brave"))
        self.set_child(GraphicChar(None, colors.WHITE, icon.GUNSLINGER_THIN))
        self.set_child(StatusDescriptionBar())
        self.set_child(CharPrinter())

        self.set_child(HealthModifier())
        self.set_child(BleedWhenDamaged())

        self.set_child(PlayerThrowStoneAction())

        self.set_child(DungeonMask())
        self.set_child(Vision())
        self.set_child(AwarenessChecker())

        self.set_child(MemoryMap())
        self.set_child(Inventory())
        self.set_child(InputActor())
        self.set_child(Path())
        self.set_child(Equipment())
        self.set_child(EffectQueue())
        self.set_child(PickUpItemAction())
        self.set_child(LeaveCorpseOnDeath())
