from action import PickUpItemAction
from attacker import Attacker, Dodger
from compositecore import Composite
from dungeonmask import DungeonMask
from entityeffect import EffectQueue
from graphic import CharPrinter, GraphicChar
from health import Health, HealthModifier
from inputactor import InputActor
from inventory import Inventory
from memorymap import MemoryMap
from mover import EntityMover
from ondeathaction import DoNothingDeathAction
from position import Position, DungeonLevel
from stats import AttackSpeed, Faction, GameState, GamePieceType
from stats import MovementSpeed, Strength, IsPlayer, Evasion, Hit
from statusflags import StatusFlags
from text import Description
from vision import Vision, SightRadius
import colors
import equipment
import gametime
import symbol


class Player(Composite):
    """
    A composite component representing the player character.
    """
    def __init__(self, game_state):
        super(Player, self).__init__()
        self.add_child(GamePieceType(GamePieceType.ENTITY))
        self.add_child(IsPlayer())

        self.add_child(Position())
        self.add_child(DungeonLevel())

        self.add_child(EntityMover())
        self.add_child(Attacker())
        self.add_child(Dodger())
        self.add_child(Evasion(12))
        self.add_child(Hit(15))

        self.add_child(Description("CO", "The Brave"))
        self.add_child(GraphicChar(None, colors.WHITE,
                                   symbol.GUNSLINGER_THIN))
        self.add_child(CharPrinter())

        self.add_child(Faction(Faction.PLAYER))
        self.add_child(Health(20))
        self.add_child(HealthModifier())
        self.add_child(Strength(4))
        self.add_child(MovementSpeed(gametime.single_turn))
        self.add_child(AttackSpeed(gametime.single_turn))
        self.add_child(StatusFlags([StatusFlags.CAN_OPEN_DOORS]))

        self.add_child(DungeonMask())
        self.add_child(SightRadius(6))
        self.add_child(Vision())

        self.add_child(MemoryMap())
        self.add_child(Inventory())
        self.add_child(InputActor())
        self.add_child(GameState(game_state))
        self.add_child(equipment.Equipment())
        self.add_child(EffectQueue())
        self.add_child(PickUpItemAction())
        self.add_child(DoNothingDeathAction())
