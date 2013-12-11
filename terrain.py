from compositecore import Leaf, Composite
from graphic import GraphicChar, CharPrinter, GraphicCharTerrainCorners
from mover import Mover
from position import Position, DungeonLevel
from stats import GamePieceType
from statusflags import StatusFlags
import colors
import icon


class TerrainFactory(object):
    def __init__(self):
        self.wall = None
        self.floor = None

    def get_wall(self):
        if self.wall is None:
            self.wall = Wall()
        return self.wall

    def get_floor(self):
        if self.floor is None:
            self.floor = Floor()
        return self.floor


terrain_factory = TerrainFactory()


class IsSolid(Leaf):
    def __init__(self, is_solid=True):
        super(IsSolid, self).__init__()
        self.component_type = "is_solid"
        self.value = is_solid

class IsChasm(Leaf):
    def __init__(self, is_chasm=True):
        super(IsChasm, self).__init__()
        self.component_type = "is_chasm"
        self.value = is_chasm

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
        self.add_child(DungeonLevel())
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
        self.add_child(DungeonLevel())
        self.add_child(GraphicChar(colors.BLUE_D,
                                   colors.BLUE,
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
        self.add_child(DungeonLevel())
        self.add_child(GraphicChar(colors.FLOOR_BG, colors.WHITE, icon.GLASS_WALL))
        self.add_child(CharPrinter())
        self.add_child(IsSolid(True))
        self.add_child(IsTransparent(True))


class Chasm(Composite):
    def __init__(self):
        super(Chasm, self).__init__()
        self.add_child(GamePieceType(GamePieceType.TERRAIN))
        self.add_child(Mover())
        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(GraphicChar(colors.DARK_GRAY, colors.DARK_GREEN, icon.CHASM + 1))
        self.add_child(CharPrinter())
        self.add_child(IsChasm(True))
        self.add_child(IsSolid(False))
        self.add_child(IsTransparent(True))


class Unknown(Composite):
    def __init__(self):
        super(Unknown, self).__init__()
        self.add_child(GamePieceType(GamePieceType.TERRAIN))
        self.add_child(Mover())
        self.add_child(Position())
        self.add_child(DungeonLevel())
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
        self.add_child(DungeonLevel())
        self.add_child(CharPrinter())
        self.add_child(GraphicCharTerrainCorners(colors.FLOOR_BG,
                                                 colors.WALL_FG,
                                                 icon.DUNGEON_WALLS_ROW,
                                                 [Wall, Door, Chasm]))
        self.add_child(IsSolid(True))
        self.add_child(IsTransparent(False))


class Door(Composite):
    def __init__(self):
        super(Door, self).__init__()
        self.add_child(GamePieceType(GamePieceType.TERRAIN))
        self.add_child(Mover())
        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(CharPrinter())
        self.add_child(GraphicChar(colors.FLOOR_BG,
                                   colors.ORANGE_D,
                                   icon.DOOR))
        self.add_child(IsSolid(True))
        self.add_child(IsTransparent(False))

        self.add_child(OpenDoorAction())
        self.add_child(OpenDoorBumpAction())
        self.add_child(IsDoor())


class IsDoor(Leaf):
    def __init__(self):
        super(IsDoor, self).__init__()
        self.component_type = "is_door"


class OpenDoorAction(Leaf):
    """Opens the door terrain."""
    def __init__(self):
        super(OpenDoorAction, self).__init__()
        self.component_type = "open_door_action"

    def open_door(self):
        self.parent.is_solid.value = False
        self.parent.is_transparent.value = True
        self.parent.graphic_char.icon = icon.DOOR_OPEN
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
