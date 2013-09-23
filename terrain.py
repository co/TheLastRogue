import colors
import icon
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
        self.gfx_char.color_fg = colors.WALL_FG
        self.gfx_char.color_bg = colors.FLOOR_BG
        self._wall_symbol_row = icon.DUNGEON_WALLS_ROW

    @staticmethod
    def is_solid():
        return True

    def on_draw(self):
        self.calculate_wall_symbol()

    def calculate_wall_symbol(self):
        neighbours_mask = 0
        for index, neighbour in enumerate(self._get_neighbour_terrains()):
            if(isinstance(neighbour, Wall) or isinstance(neighbour, Door)):
                neighbours_mask |= 2 ** index
        self.gfx_char.symbol = self._wall_symbol_row + neighbours_mask

    def is_transparent(self):
        return False

    def _get_neighbour_terrains(self):
        tiles =\
            self.dungeon_level.get_tiles_surrounding_position(self.position)
        return [tile.get_terrain() for tile in tiles]


class Floor(Terrain):
    def __init__(self):
        super(Floor, self).__init__()
        self.gfx_char.color_fg = colors.FLOOR_FG
        self.gfx_char.color_bg = colors.FLOOR_BG
        self.gfx_char.symbol = icon.CENTER_DOT


class Water(Terrain):
    def __init__(self):
        super(Water, self).__init__()
        self.gfx_char.color_fg = colors.BLUE_D
        self.gfx_char.color_bg = colors.CYAN_D
        self.gfx_char.symbol = icon.WATER


class Door(Terrain):
    def __init__(self, is_open=True):
        super(Door, self).__init__()
        self.is_open = is_open
        self.gfx_char.color_fg = colors.ORANGE_D
        self.gfx_char.color_bg = colors.FLOOR_BG

    def is_solid(self):
        return not self.is_open

    @property
    def is_open(self):
        return self.__is_open

    @is_open.setter
    def is_open(self, value):
        self.__is_open = value
        if(self.__is_open):
            self.gfx_char.symbol = icon.DOOR_OPEN
        else:
            self.gfx_char.symbol = icon.DOOR
        if(not self.dungeon_level is None):
            self.dungeon_level.signal_terrain_changed()

    @property
    def symbol(self):
        if(self.is_open):
            return icon.DOOR_OPEN
        else:
            return icon.DOOR

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
        self.gfx_char.color_fg = colors.WHITE
        self.gfx_char.symbol = icon.CAVE_WALLS_ROW

    @staticmethod
    def is_transparent():
        return True


class Unknown(Terrain):
    def __init__(self):
        super(Unknown, self).__init__()
        self.gfx_char.color_fg = colors.BLACK
        self.gfx_char.color_bg = colors.BLACK
        self.gfx_char.symbol = ' '

    @property
    def symbol(self):
        return ' '
