import Colors as colors
import libtcodpy as libtcod


class Terrain(object):

    def __init__(self, position):
        self.position = position

    @staticmethod
    def GetColorBG():
        return colors.UNINITIALIZED_BG

    @staticmethod
    def GetColorFG():
        return colors.UNINITIALIZED_FG

    @staticmethod
    def IsSolid():
        return False

    @staticmethod
    def GetSymbol():
        return '?'

    @staticmethod
    def IsTransparent():
        return True

    def Draw(self, isSeen):
        if(isSeen):
            libtcod.console_put_char_ex(0, self.position[0], self.position[1],
                                        self.GetSymbol(), self.GetColorFG(),
                                        self.GetColorBG())
        else:
            libtcod.console_put_char_ex(0, self.position[0],
                                        self.position[1],
                                        self.GetSymbol(),
                                        colors.PURPLE_SHADOW_DARK,
                                        colors.BLACK)


class Wall(Terrain):

    def __init__(self, position):
        super(Wall, self).__init__(position)

    @staticmethod
    def GetColorBG():
        return colors.WALL_BG

    @staticmethod
    def GetColorFG():
        return colors.FLOOR_FG

    @staticmethod
    def GetSymbol():
        return '#'

    @staticmethod
    def IsSolid():
        return True

    def IsTransparent(self):
        return False


class Floor(Terrain):

    def __init__(self, position):
        super(Floor, self).__init__(position)

    @staticmethod
    def GetColorBG():
        return colors.FLOOR_BG

    @staticmethod
    def GetColorFG():
        return colors.FLOOR_FG

    @staticmethod
    def GetSymbol():
        return '.'


class Water(Terrain):

    def __init__(self, position):
        super(Water, self).__init__(position)

    def GetSymbol():
        return '~'


class Door(Terrain):

    def __init__(self, position, isOpen):
        super(Door, self).__init__(position)
        self.IsOpen = isOpen

    def GetSymbol(self):
        if(self.IsOpen):
            return "'"
        else:
            return "+"

    def IsTransparent(self):
        if self.IsOpen:
            return True
        else:
            return False

    def Close(self):
        self.isOpen = False

    def Open(self):
        self.isOpen = True
