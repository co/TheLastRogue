import colors
import symbol
import gamepiece


class Terrain(gamepiece.GamePiece):
    def __init__(self):
        super(Terrain, self).__init__()
        self.max_instances_in_single_tile = 1
        self.piece_type = gamepiece.GamePieceType.TERRAIN

    @staticmethod
    def is_solid():
        return False

    @staticmethod
    def is_transparent():
        return True


class Wall (Terrain):
    def __init__(self):
        super(Wall, self).__init__()
        self._color_fg = colors.WALL_FG
        self._color_bg = colors.FLOOR_BG
        self._symbol = symbol.DUNGEON_WALLS_ROW

    @staticmethod
    def is_solid():
        return True

    @property
    def symbol(self):
        neighbours_mask = 0
        for index, neighbour in enumerate(self._get_neighbour_terrains()):
            if(isinstance(neighbour, Wall) or isinstance(neighbour, Door)):
                neighbours_mask |= 2 ** index
        return self._symbol + neighbours_mask

    def is_transparent(self):
        return False

    def _get_neighbour_terrains(self):
        tiles =\
            self.dungeon_level.get_tiles_surrounding_position(self.position)
        return [tile.get_terrain() for tile in tiles]


class Floor(Terrain):
    def __init__(self):
        super(Floor, self).__init__()
        self._color_fg = colors.FLOOR_FG
        self._color_bg = colors.FLOOR_BG
        self._symbol = symbol.CENTER_DOT


class Water(Terrain):
    def __init__(self):
        super(Water, self).__init__()
        self._color_fg = colors.BLUE_D
        self._color_bg = colors.CYAN_D
        self._symbol = symbol.WATER


class Door(Terrain):
    def __init__(self, is_open=True):
        super(Door, self).__init__()
        self.__is_open = is_open
        self._color_fg = colors.ORANGE_D
        self._color_bg = colors.FLOOR_BG

    def is_solid(self):
        return not self.is_open

    @property
    def is_open(self):
        return self.__is_open

    @is_open.setter
    def is_open(self, value):
        self.__is_open = value
        self.dungeon_level.signal_terrain_changed()

    @property
    def symbol(self):
        if(self.is_open):
            return symbol.DOOR_OPEN
        else:
            return symbol.DOOR

    def is_transparent(self):
        return self.is_open

    def close(self):
        self.is_open = False

    def open(self):
        self.is_open = True

    def piece_copy(self, copy=None):
        if(copy is None):
            copy = Door(self.is_open)
        return super(Door, self).piece_copy(copy)


class GlassWall(Wall):
    def __init__(self):
        super(GlassWall, self).__init__()
        self._color_fg = colors.WHITE
        self._symbol = symbol.CAVE_WALLS_ROW

    @staticmethod
    def is_transparent():
        return True


class Unknown(Terrain):
    def __init__(self):
        super(Unknown, self).__init__()
        self._color_fg = colors.BLACK
        self._color_bg = colors.BLACK

    @property
    def symbol(self):
        return ' '
