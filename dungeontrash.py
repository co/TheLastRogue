import gamepiece
import colors
import symbol


class DungeonTrash(gamepiece.GamePiece):
    """
    An item that appears in the dungeon with almost no practical use.
    Since it is so useless the player won't be allowed to pick it up.

    piece_type (GamePieceType): Denotes that Item and all its
                                subclasses is of type ITEM.
    max_instances_in_single_tile: The number of allowed pieces of this types
                                  on a tile.
    """
    def __init__(self):
        super(DungeonTrash, self).__init__()
        self.piece_type = gamepiece.GamePieceType.DUNGEON_TRASH
        self.max_instances_in_single_tile = 1
        self._name = "XXX_UNNAMED_XXX"
        self._description = "XXX_DESCRIPTION_XXX"


class Corpse(DungeonTrash):
    """
    A corpse. Totally useless but looks nice
    and gives the user feedback when a monster dies.
    """
    def __init__(self):
        super(Corpse, self).__init__()
        self.gfx_char.color_fg = colors.WHITE
        self.gfx_char.symbol = symbol.CORPSE
        self._name = "A rottening corpse."
        self._description = "A rottening corpse."
