import random
from compositecore import Composite
from graphic import GraphicChar, CharPrinter
import icon
from mover import Mover
from position import Position, DungeonLevel
from stats import GamePieceType
from text import Description
import colors


class Corpse(Composite):
    """
    A corpse. Totally useless but looks nice
    and gives the user feedback when a monster dies.
    """
    def __init__(self):
        super(Corpse, self).__init__()
        self.add_child(GamePieceType(GamePieceType.DUNGEON_TRASH))
        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(Description("A rotting corpse.",
                                   "A rotting corpse."))
        self.add_child(GraphicChar(None, colors.WHITE,
                                   icon.CORPSE))
        self.add_child(CharPrinter())
        self.add_child(Mover())


class PoolOfBlood(Composite):
    """
    A pool of blood. Totally useless but looks nice
    and gives the user feedback when a monster is hurt.
    """
    def __init__(self):
        super(PoolOfBlood, self).__init__()
        self.add_child(GamePieceType(GamePieceType.DUNGEON_TRASH))
        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(Description("A pool of blood.",
                                   "A pool of blood."))
        self.add_child(GraphicChar(None, colors.RED,
                                   random.choice(icon.BLOOD_ICONS)))
        self.add_child(CharPrinter())
        self.add_child(Mover())
