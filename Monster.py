import Counter as counter
import Colors as colors
import libtcodpy as libtcod


class Monster(object):

    def __init__(self, dungeon_location):
        self.hp = counter.Counter(1, 1)
        self.dungeon_location = dungeon_location
        self.fov_map = None

    @staticmethod
    def get_color_fg():
        return colors.UNINITIALIZED_FG

    @staticmethod
    def get_symbol():
        return '?'

    def update(self, dungeon_level, player):
        pass

    def draw(self, isSeen):
        position = self.dungeon_location.position
        if(isSeen):
            libtcod.console_put_char_ex(0, position[0], position[1],
                                        self.get_symbol(),
                                        self.get_color_fg(),
                                        self.get_color_bg())
        else:
            libtcod.console_put_char_ex(0, position[0], position[1],
                                        self.get_symbol(),
                                        colors.UNSEEN_FG,
                                        colors.UNSEEN_BG)


class RatMan(Monster):
    def __init__(self, dungeon_location):
        super(RatMan, self).__init__(dungeon_location)
        self.hp = counter.Counter(10, 10)

    @staticmethod
    def get_symbol():
        return 'r'

    @staticmethod
    def get_color_fg():
        return colors.DB_OILED_CEDAR
