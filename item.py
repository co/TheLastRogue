import colors
import gamepiece


class Item(gamepiece.GamePiece):
    def __init__(self):
        super(Item, self).__init__()

        self.piece_type = gamepiece.ITEM_GAME_PIECE
        self.max_instances_in_single_tile = 1
        self.draw_order = 1
        pass

    @staticmethod
    def get_name():
        return "XXX_UNNAMED_XXX"

    @staticmethod
    def get_description():
        return "XXX_DESCRIPTION_XXX"


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
