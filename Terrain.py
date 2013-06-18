import Colors as colors
import libtcodpy as libtcod


class Terrain(object):

    def __init__(self):
        pass

    @staticmethod
    def get_color_bg():
        return colors.UNINITIALIZED_BG

    @staticmethod
    def get_color_fg():
        return colors.UNINITIALIZED_FG

    @staticmethod
    def is_solid():
        return False

    @staticmethod
    def get_symbol():
        return '?'

    @staticmethod
    def is_transparent():
        return True

    def draw(self, position, is_seen):
        if(is_seen):
            fg_color = self.get_color_fg()
            bg_color = self.get_color_bg()
        else:
            fg_color = colors.UNSEEN_FG
            bg_color = colors.UNSEEN_BG

        x = position[0]
        y = position[1]
        libtcod.console_set_char_foreground(0, x, y, fg_color)
        libtcod.console_set_char_background(0, x, y, bg_color)
        libtcod.console_set_char(0, x, y, self.get_symbol())


class Wall(Terrain):

    def __init__(self):
        super(Wall, self).__init__()

    @staticmethod
    def get_color_bg():
        return colors.WALL_BG

    @staticmethod
    def get_color_fg():
        return colors.WALL_FG

    @staticmethod
    def get_symbol():
        return '#'

    @staticmethod
    def is_solid():
        return True

    def is_transparent(self):
        return False


class Floor(Terrain):

    def __init__(self):
        super(Floor, self).__init__()

    @staticmethod
    def get_color_bg():
        return colors.DB_LOULOU

    @staticmethod
    def get_color_fg():
        return colors.DB_STINGER

    @staticmethod
    def get_symbol():
        return '.'


class Water(Terrain):

    def __init__(self):
        super(Water, self).__init__()

    @staticmethod
    def get_color_bg():
        return colors.DB_VENICE_BLUE

    @staticmethod
    def get_color_fg():
        return colors.DB_CORNFLOWER

    @staticmethod
    def get_symbol():
        return '~'


class Door(Terrain):

    def __init__(self, is_open):
        super(Door, self).__init__()
        self.is_open = is_open

    @staticmethod
    def get_color_bg():
        return colors.DB_OILED_CEDAR

    @staticmethod
    def get_color_fg():
        return colors.DB_ROPE

    def is_solid(self):
        return not self.is_open

    def get_symbol(self):
        if(self.is_open):
            return "'"
        else:
            return "+"

    def is_transparent(self):
        if self.is_open:
            return True
        else:
            return False

    def close(self):
        self.is_open = False

    def open(self):
        self.is_open = True


class GlassWall(Wall):

    def __init__(self):
        super(GlassWall, self).__init__()

    @staticmethod
    def get_color_bg():
        return colors.DB_HEATHER

    @staticmethod
    def get_color_fg():
        return colors.DB_LIGHT_STEEL_BLUE

    @staticmethod
    def is_transparent():
        return True

    @staticmethod
    def get_symbol():
        return libtcod.CHAR_DIAMOND


class Unknown(Terrain):

    def __init__(self):
        super(Unknown, self).__init__()

    @staticmethod
    def get_color_bg():
        return colors.BLACK

    @staticmethod
    def get_color_fg():
        return colors.BLACK

    @staticmethod
    def get_symbol():
        return ' '
