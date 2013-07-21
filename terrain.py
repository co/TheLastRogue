import colors
import gamepiece
import libtcodpy as libtcod


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


class Wall(Terrain):
    def __init__(self):
        super(Wall, self).__init__()
        self._color_fg = colors.WALL_FG
        self._color_bg = colors.WALL_BG
        self._symbol = '#'

    @staticmethod
    def is_solid():
        return True

    def is_transparent(self):
        return False


class Floor(Terrain):
    def __init__(self):
        super(Floor, self).__init__()
        self._color_fg = colors.DB_STINGER
        self._color_bg = colors.DB_LOULOU
        self._symbol = '.'


class Water(Terrain):
    def __init__(self):
        super(Water, self).__init__()
        self._color_fg = colors.DB_CORNFLOWER
        self._color_bg = colors.DB_VENICE_BLUE
        self._symbol = '~'


class Door(Terrain):
    def __init__(self, is_open=True):
        super(Door, self).__init__()
        self.__is_open = is_open
        self._color_fg = colors.DB_ROPE
        self._color_bg = colors.DB_OILED_CEDAR

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
            return "'"
        else:
            return "+"

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
        self._color_fg = colors.DB_LIGHT_STEEL_BLUE
        self._color_bg = colors.DB_HEATHER
        self._symbol = libtcod.CHAR_DIAMOND

    @staticmethod
    def is_transparent():
        return True


class Unknown(Terrain):
    def __init__(self):
        super(Unknown, self).__init__()
        self._color_fg = colors.DB_BLACK
        self._color_bg = colors.DB_BLACK

    @property
    def symbol(self):
        return ' '
