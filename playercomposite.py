from position import Position
from dungeonlevelcomposite import DungeonLevel
from statusflags import StatusFlags
from compositecore import Composite
from sightradius import SightRadius
from dungeonmask import DungeonMask
from gamepiecetype import GamePieceType
from memorymap import MemoryMap
from composite import Description, GraphicChar, MovementSpeed, IsPlayer
from composite import Health, Strength, AttackSpeed, Faction, Inventory
from mover import Mover
import gametime
import symbol
import colors


class Player(Composite):
    """
    A composite component representing the player character.
    """
    def __init__(self):
        super(Player, self).__init__()
        self.add_child(IsPlayer())
        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(Description())
        self.add_child(GraphicChar(symbol.GUNSLINGER_THIN,
                                   None, colors.WHITE))

        self.add_child(Health(10))
        self.add_child(Strength(10))
        self.add_child(MovementSpeed(gametime.single_turn))
        self.add_child(AttackSpeed(gametime.single_turn))
        self.add_child(Faction(Faction.PLAYER))
        self.add_child(SightRadius(6))
        self.add_child(StatusFlags())
        self.add_child(DungeonMask())
        self.add_child(MemoryMap())
        self.add_child(Inventory())
        self.add_child(Mover())
        self.add_child(GamePieceType(GamePieceType.ENTITY))
        #self.add_child(equipment.Equipment(6))
