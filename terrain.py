from compositecore import Leaf, Composite
from graphic import GraphicChar, CharPrinter, GraphicCharTerrainCorners
from mover import Mover
from position import Position, DungeonLevel
from stats import GamePieceType, Flag
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


class BumpAction(Leaf):
    """
    Defines what happens if the player bumps into this terrain.
    """
    def __init__(self):
        super(BumpAction, self).__init__()
        self.component_type = "bump_action"

    def bump(self, source_entity):
        pass

    def can_bump(self, source_entity):
        return True


class Floor(Composite):
    def __init__(self):
        super(Floor, self).__init__()
        self.set_child(GamePieceType(GamePieceType.TERRAIN))
        self.set_child(Mover())
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(GraphicChar(colors.FLOOR_BG,
                                   colors.FLOOR_FG,
                                   icon.CENTER_DOT))
        self.set_child(CharPrinter())
        self.set_child(Flag("is_transparent"))


class Water(Composite):
    def __init__(self):
        super(Water, self).__init__()
        self.set_child(GamePieceType(GamePieceType.TERRAIN))
        self.set_child(Mover())
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(GraphicChar(colors.BLUE_D,
                                   colors.BLUE,
                                   icon.WATER))
        self.set_child(CharPrinter())
        self.set_child(Flag("is_transparent"))


class GlassWall(Composite):
    def __init__(self):
        super(GlassWall, self).__init__()
        self.set_child(GamePieceType(GamePieceType.TERRAIN))
        self.set_child(Mover())
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(GraphicChar(colors.FLOOR_BG, colors.WHITE, icon.GLASS_WALL))
        self.set_child(CharPrinter())
        self.set_child(Flag("is_solid"))
        self.set_child(Flag("is_transparent"))


class Chasm(Composite):
    def __init__(self):
        super(Chasm, self).__init__()
        self.set_child(GamePieceType(GamePieceType.TERRAIN))
        self.set_child(Mover())
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(GraphicChar(colors.DARKNESS, colors.DARK_GREEN, icon.CHASM2))
        self.set_child(CharPrinter())
        self.set_child(Flag("is_chasm"))
        self.set_child(Flag("is_transparent"))


class Unknown(Composite):
    def __init__(self):
        super(Unknown, self).__init__()
        self.set_child(GamePieceType(GamePieceType.TERRAIN))
        self.set_child(Mover())
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(CharPrinter())
        self.set_child(GraphicChar(colors.BLACK,
                                   colors.BLACK,
                                   ' '))
        self.set_child(Flag("is_solid"))
        self.set_child(Flag("is_transparent"))


class Wall (Composite):
    def __init__(self):
        super(Wall, self).__init__()
        self.set_child(GamePieceType(GamePieceType.TERRAIN))
        self.set_child(Mover())
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(CharPrinter())
        self.set_child(GraphicCharTerrainCorners(colors.FLOOR_BG,
                                                 colors.WALL_FG,
                                                 icon.DUNGEON_WALLS_ROW,
                                                 [Wall, Door, Chasm]))
        self.set_child(Flag("is_solid"))


class Door(Composite):
    def __init__(self):
        super(Door, self).__init__()
        self.set_child(GamePieceType(GamePieceType.TERRAIN))
        self.set_child(Mover())
        self.set_child(Position())
        self.set_child(DungeonLevel())
        self.set_child(CharPrinter())
        self.set_child(GraphicChar(colors.FLOOR_BG,
                                   colors.ORANGE_D,
                                   icon.DOOR))
        self.set_child(Flag("is_solid"))

        self.set_child(OpenDoorAction())
        self.set_child(OpenDoorBumpAction())
        self.set_child(Flag("is_door"))


class OpenDoorAction(Leaf):
    """Opens the door terrain."""
    def __init__(self):
        super(OpenDoorAction, self).__init__()
        self.component_type = "open_door_action"

    def open_door(self):
        if self.parent.has("is_solid"):
            self.parent.remove_component_of_type("is_solid")
        self.parent.set_child(Flag("is_transparent"))
        self.parent.graphic_char.icon = icon.DOOR_OPEN
        self.parent.dungeon_level.value.signal_terrain_changed()


class OpenDoorBumpAction(BumpAction):
    """
    Defines what happens if the player bumps into this terrain.
    """
    def __init__(self):
        super(OpenDoorBumpAction, self).__init__()
        self.component_type = "bump_action"

    def bump(self, source_entity):
        self.parent.open_door_action.open_door()

    def can_bump(self, source_entity):
        return (self.parent.has("is_solid") and
                (source_entity.status_flags.
                 has_status(StatusFlags.CAN_OPEN_DOORS)))
