import Colors as colors
import libtcodpy as libtcod


class Terrain(object):

    def __init__(self, position):
        self.position = position

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

    def draw(self, isSeen):
        if(isSeen):
            libtcod.console_put_char_ex(0, self.position[0], self.position[1],
                                        self.get_symbol(), self.get_color_fg(),
                                        self.get_color_bg())
        else:
            libtcod.console_put_char_ex(0, self.position[0],
                                        self.position[1],
                                        self.get_symbol(),
                                        colors.PURPLE_SHADOW_DARK,
                                        colors.BLACK)


class Wall(Terrain):

    def __init__(self, position):
        super(Wall, self).__init__(position)

    @staticmethod
    def get_color_bg():
        return colors.WALL_BG

    @staticmethod
    def get_color_fg():
        return colors.FLOOR_FG

    @staticmethod
    def get_symbol():
        return '#'

    @staticmethod
    def is_solid():
        return True

    def is_transparent(self):
        return False


class Floor(Terrain):

    def __init__(self, position):
        super(Floor, self).__init__(position)

    @staticmethod
    def get_color_bg():
        return colors.FLOOR_BG

    @staticmethod
    def get_color_fg():
        return colors.FLOOR_FG

    @staticmethod
    def get_symbol():
        return '.'


class Water(Terrain):

    def __init__(self, position):
        super(Water, self).__init__(position)

    def get_symbol():
        return '~'


class Door(Terrain):

    def __init__(self, position, isOpen):
        super(Door, self).__init__(position)
        self.IsOpen = isOpen

    def get_symbol(self):
        if(self.IsOpen):
            return "'"
        else:
            return "+"

    def is_transparent(self):
        if self.IsOpen:
            return True
        else:
            return False

    def Close(self):
        self.isOpen = False

    def Open(self):
        self.isOpen = True


class Unknown(Terrain):

    def __init__(self, position):
        super(Unknown, self).__init__(position)

    @staticmethod
    def get_color_bg():
        return colors.BLACK

    @staticmethod
    def get_color_fg():
        return colors.BLACK

    @staticmethod
    def get_symbol():
        return ' '
