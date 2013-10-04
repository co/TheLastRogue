from composite import Description, GraphicChar, CharPrinter
from position import Position
from dungeonlevelcomposite import DungeonLevel
from compositecore import Composite
from gamepiecetype import GamePieceType
import colors
import symbol


class Corpse(Composite):
    """
    A corpse. Totally useless but looks nice
    and gives the user feedback when a monster dies.
    """
    def __init__(self):
        super(Corpse, self).__init__()
        self.add_child(GamePieceType(GamePieceType.DUNGEON_FEATURE))
        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(Description("A routeing corpse.",
                                   "A rotting corpse."))
        self.add_child(GraphicChar(symbol.CORPSE,
                                   None, colors.WHITE))
        self.add_child(CharPrinter)
