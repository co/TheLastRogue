import colors
import action
import gamepiece


class Item(gamepiece.GamePiece):
    def __init__(self):
        super(Item, self).__init__()

        self.piece_type = gamepiece.ITEM_GAME_PIECE
        self.max_instances_in_single_tile = 1
        self.draw_order = 1
        self._name = "XXX_UNNAMED_XXX"
        self._description = "XXX_DESCRIPTION_XXX"
        self.inventory = None
        self.actions = []


class Gun(Item):
    def __init__(self):
        super(Gun, self).__init__()
        self._color_fg = colors.DB_WHITE
        self._color_bg = None
        self._symbol = ord('(')
        self._name = "Gun"
        self._description =\
            "This was once a fine weapon, but age has torn it real bad.\n\
            The wooden handle is dry and gray \
            and you see rust eating into the iron pipe."


class Potion(Item):
    def __init__(self):
        super(Potion, self).__init__()
        self._symbol = ord('?')
        self._name = "XXX_Potion_XXX"
        self._description =\
            "An unusual liquid contained in a glass flask."


class HealthPotion(Potion):
    def __init__(self):
        super(Potion, self).__init__()
        self._color_fg = colors.DB_PLUM
        self._name = "Health Potion"
        self._description =\
            "An unusual liquid contained in a glass flask."
        self.actions.append(action.HealingPotionDrink(self))
