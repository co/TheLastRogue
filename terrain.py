import colors
import icon
from gamepiecetype import GamePieceType
from composite import GraphicChar, CharPrinter, GraphicCharTerrainCorners
from compositecore import Leaf, Composite
from mover import Mover
from position import Position
from statusflags import StatusFlags


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


class BumpAction(Leaf):
    """
    Defines what happens if the player bumps into this terrain.
    """
    def __init__(self, is_transparent=False):
        super(BumpAction, self).__init__()
        self.component_type = "bump_action"

    def bump(self, source_entity):
        pass

    def can_bump(self, source_entity):
        return True


class Floor(Composite):
    def __init__(self):
        super(Floor, self).__init__()
        self.add_child(GamePieceType(GamePieceType.TERRAIN))
        self.add_child(Mover())
        self.add_child(Position())
        self.add_child(GraphicChar(colors.FLOOR_BG,
                                   colors.FLOOR_FG,
                                   icon.CENTER_DOT))
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
        self.add_child(GraphicChar(colors.FLOOR_BG,
                                   colors.WHITE,
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
        self.add_child(GraphicCharTerrainCorners(colors.FLOOR_BG,
                                                 colors.WALL_FG,
                                                 icon.DUNGEON_WALLS_ROW,
                                                 [Wall, Door]))
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
        self.add_child(GraphicChar(colors.FLOOR_BG,
                                   colors.ORANGE_D,
                                   icon.DOOR))
        self.add_child(IsSolid(True))
        self.add_child(IsTransparent(False))

        self.add_child(OpenDoorAction())
        self.add_child(OpenDoorBumpAction())


class OpenDoorAction(Leaf):
    """Opens the door terrain."""
    def __init__(self):
        super(OpenDoorAction, self).__init__()
        self.component_type = "open_door_action"

    def open_door(self):
        print "time to open door!"
        self.parent.is_solid.value = False
        self.parent.is_transparent.value = True
        self.parent.graphic_char.symbol = icon.DOOR_OPEN
        self.parent.dungeon_level.value.signal_terrain_changed()


class OpenDoorBumpAction(BumpAction):
    """
    Defines what happens if the player bumps into this terrain.
    """
    def __init__(self, is_transparent=False):
        super(OpenDoorBumpAction, self).__init__()
        self.component_type = "bump_action"

    def bump(self, source_entity):
        self.parent.open_door_action.open_door()

    def can_bump(self, source_entity):
        return (self.parent.is_solid.value and
                (source_entity.status_flags.
                 has_status(StatusFlags.CAN_OPEN_DOORS)))

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
