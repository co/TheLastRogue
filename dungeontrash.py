import random
from compositecore import Composite
from graphic import GraphicChar, CharPrinter
import icon
from mover import Mover
from position import Position, DungeonLevel
from stats import GamePieceTypes, DataTypes, DataPoint
from text import Description
import colors


class Corpse(Composite):
    """
    A corpse. Totally useless but looks nice
    and gives the user feedback when a monster dies.
    """
    def __init__(self):
        super(Corpse, self).__init__()
        self.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.DUNGEON_TRASH))
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(Description("A rotting corpse.",
                                   "A rotting corpse."))
        self.set_child(GraphicChar(None, colors.WHITE,
                                   icon.CORPSE))
        self.set_child(CharPrinter())
        self.set_child(Mover())


class PoolOfBlood(Composite):
    """
    A pool of blood. Totally useless but looks nice
    and gives the user feedback when a monster is hurt.
    """
    def __init__(self):
        super(PoolOfBlood, self).__init__()
        self.set_child(DataPoint(DataTypes.GAME_PIECE_TYPE, GamePieceTypes.DUNGEON_TRASH))
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(Description("A pool of blood.", "A pool of blood."))
        self.set_child(GraphicChar(None, colors.RED, random.choice(icon.BLOOD_ICONS)))
        self.set_child(CharPrinter())
        self.set_child(Mover())
