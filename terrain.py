import colors
import icon
from gamepiecetype import GamePieceType
from composite import GraphicChar, CharPrinter
from compositecore import Leaf, Composite
from mover import Mover
from position import Position


class IsSolid(Leaf):
    def __init__(self, is_solid=True):
        super(IsSolid, self).__init__()
        self.component_type = "is_solid"
        self.value = is_solid


class IsTransparent(Leaf):
    def __init__(self, is_transparent=False):
        super(IsTransparent, self).__init__()
        self.component_type = "is_transparent"
        self.value = is_transparent


class Floor(Composite):
    def __init__(self):
        super(Floor, self).__init__()
        self.add_child(GamePieceType(GamePieceType.TERRAIN))
        self.add_child(Mover())
        self.add_child(Position())
        self.add_child(GraphicChar(colors.FLOOR_BG,
                                   colors.FLOOR_FG,
                                   "."))
        self.add_child(CharPrinter())
        self.add_child(IsSolid(False))
        self.add_child(IsTransparent(True))


class Water(Composite):
    def __init__(self):
        super(Water, self).__init__()
        self.add_child(GamePieceType(GamePieceType.TERRAIN))
        self.add_child(Mover())
        self.add_child(Position())
        self.add_child(GraphicChar(colors.BLUE_D,
                                   colors.CYAN_D,
                                   icon.WATER))
        self.add_child(CharPrinter())
        self.add_child(IsSolid(False))
        self.add_child(IsTransparent(True))


class GlassWall(Composite):
    def __init__(self):
        super(GlassWall, self).__init__()
        self.add_child(GamePieceType(GamePieceType.TERRAIN))
        self.add_child(Mover())
        self.add_child(Position())
        self.add_child(GraphicChar(colors.WHITE,
                                   colors.FLOOR_BG,
                                   icon.CAVE_WALLS_ROW))
        self.add_child(CharPrinter())
        self.add_child(IsSolid(True))
        self.add_child(IsTransparent(True))


class Unknown(Composite):
    def __init__(self):
        super(Unknown, self).__init__()
        self.add_child(GamePieceType(GamePieceType.TERRAIN))
        self.add_child(Mover())
        self.add_child(Position())
        self.add_child(CharPrinter())
        self.add_child(GraphicChar(colors.BLACK,
                                   colors.BLACK,
                                   ' '))
        self.add_child(IsSolid(True))
        self.add_child(IsTransparent(True))


class Wall (Composite):
    def __init__(self):
        super(Wall, self).__init__()
        self.add_child(GamePieceType(GamePieceType.TERRAIN))
        self.add_child(Mover())
        self.add_child(Position())
        self.add_child(CharPrinter())
        self.add_child(GraphicChar(colors.FLOOR_BG,
                                   colors.WALL_FG,
                                   icon.DUNGEON_WALLS_ROW))
        self.add_child(IsSolid(True))
        self.add_child(IsTransparent(False))

#    def on_draw(self):
#        self.calculate_wall_symbol()
#
#    def calculate_wall_symbol(self):
#        neighbours_mask = 0
#        for index, neighbour in enumerate(self._get_neighbour_terrains()):
#            if(isinstance(neighbour, Wall) or isinstance(neighbour, Door)):
#                neighbours_mask |= 2 ** index
#        self.gfx_char.symbol = self._wall_symbol_row + neighbours_mask
#
#    def is_transparent(self):
#        return False
#
#    def _get_neighbour_terrains(self):
#        tiles =\
#            self.dungeon_level.get_tiles_surrounding_position(self.position)
#        return [tile.get_terrain() for tile in tiles]


class Door(Composite):
    def __init__(self, is_open=True):
        super(Door, self).__init__()
        self.add_child(GamePieceType(GamePieceType.TERRAIN))
        self.add_child(Mover())
        self.add_child(Position())
        self.add_child(CharPrinter())
        self.add_child(GraphicChar(colors.ORANGE_D,
                                   colors.FLOOR_BG,
                                   icon.DUNGEON_WALLS_ROW))
        self.add_child(IsSolid(True))
        self.add_child(IsTransparent(False))


#    def is_solid(self):
#        return not self.is_open
#
#    @property
#    def is_open(self):
#        return self.__is_open
#
#    @is_open.setter
#    def is_open(self, value):
#        self.__is_open = value
#        if(self.__is_open):
#            self.gfx_char.symbol = icon.DOOR_OPEN
#        else:
#            self.gfx_char.symbol = icon.DOOR
#        if(not self.dungeon_level is None):
#            self.dungeon_level.signal_terrain_changed()
#
#    @property
#    def symbol(self):
#        if(self.is_open):
#            return icon.DOOR_OPEN
#        else:
#            return icon.DOOR
#
#    def is_transparent(self):
#        return self.is_open
#
#    def close(self):
#        self.is_open = False
#
#    def open(self):
#        self.is_open = True
#
#    def piece_copy(self, copy=None):
#        if(copy is None):
#            copy = Door(self.is_open)
#        return super(Door, self).piece_copy(copy)
