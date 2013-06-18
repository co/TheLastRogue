import Colors as colors
import libtcodpy as libtcod


class Item(object):
    def __init__(self):
        pass

    @staticmethod
    def get_color_fg():
        return colors.UNINITIALIZED_FG

    @staticmethod
    def get_symbol():
        return ord('?')

    @staticmethod
    def get_name():
        return "XXX_UNNAMED_XXX"

    @staticmethod
    def get_description():
        return "XXX_DESCRIPTION_XXX"

    def draw(self, position, is_seen):
        if(is_seen):
            fg_color = self.get_color_fg()
        else:
            fg_color = colors.UNSEEN_FG

        print(position)
        libtcod.console_set_char_foreground(0, position[0],
                                            position[1], fg_color)
        libtcod.console_set_char(0, position[0], position[1],
                                 self.get_symbol())


class Gun(Item):

    def __init__(self):
        super(Gun, self).__init__()

    @staticmethod
    def get_symbol():
        return ord('(')

    @staticmethod
    def get_color_fg():
        return colors.DB_WHITE

    @staticmethod
    def get_name():
        return "Gun"

    @staticmethod
    def get_description():
        return "This was once a fine weapon, but age has torn it real bad.\n\
                The wooden handle is dry and gray \
                and you see rust eating into the iron pipe."
