from item import PickUpItemAction
from attacker import Attacker, Dodger, ArmorChecker
from compositecore import Composite
from dungeonmask import DungeonMask, Path
from entityeffect import EffectQueue
from graphic import CharPrinter, GraphicChar
from health import Health, HealthModifier, BleedWhenDamaged
from inputactor import InputActor
from inventory import Inventory
from memorymap import MemoryMap
from missileaction import PlayerThrowStoneAction
from mover import Mover, Stepper
from ondeath import LeaveCorpseOnDeath
from position import Position, DungeonLevel
from stats import AttackSpeed, Faction, GameState, GamePieceType, Stealth, Awareness, Armor
from stats import MovementSpeed, Strength, IsPlayer, Evasion, Hit
from statusflags import StatusFlags
from text import Description
from vision import Vision, SightRadius, AwarenessChecker
import colors
import equipment
import gametime
import icon


class Player(Composite):
    """
    A composite component representing the player character.
    """
    def __init__(self, game_state):
        super(Player, self).__init__()
        self.set_child(GamePieceType(GamePieceType.ENTITY))
        self.set_child(IsPlayer())

        self.set_child(Position())
        self.set_child(DungeonLevel())

        self.set_child(Mover())
        self.set_child(Stepper())
        self.set_child(Attacker())
        self.set_child(Dodger())
        self.set_child(Evasion(15))
        self.set_child(Hit(16))
        self.set_child(Armor(4))
        self.set_child(ArmorChecker())

        self.set_child(Description("CO", "The Brave"))
        self.set_child(GraphicChar(None, colors.WHITE,
                                   icon.GUNSLINGER_THIN))
        self.set_child(CharPrinter())

        self.set_child(Health(25))
        self.set_child(HealthModifier())
        self.set_child(BleedWhenDamaged())

        self.set_child(Faction(Faction.PLAYER))
        self.set_child(Strength(5))
        self.set_child(MovementSpeed(gametime.single_turn))
        self.set_child(AttackSpeed())
        self.set_child(PlayerThrowStoneAction())
        self.set_child(StatusFlags([StatusFlags.CAN_OPEN_DOORS, StatusFlags.HAS_MIND, StatusFlags.IS_ALIVE]))

        self.set_child(DungeonMask())
        self.set_child(SightRadius(6))
        self.set_child(Vision())
        self.set_child(Stealth(6))
        self.set_child(Awareness(5))
        self.set_child(AwarenessChecker())

        self.set_child(MemoryMap())
        self.set_child(Inventory())
        self.set_child(InputActor())
        self.set_child(Path())
        self.set_child(GameState(game_state))
        self.set_child(equipment.Equipment())
        self.set_child(EffectQueue())
        self.set_child(PickUpItemAction())

        self.set_child(LeaveCorpseOnDeath())
