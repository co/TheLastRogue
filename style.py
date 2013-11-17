import icon
import colors
import libtcodpy as libtcod
from console import GrahicChar
import settings


class MenuStyle(object):
    def __init__(self, rect_style, inactive_text_color, margin):
        self.rect_style = rect_style
        self.inactive_text_color = inactive_text_color
        self.margin = margin


class RectangleStyle(object):
    def __init__(self):
        self.center = None

        self.top = None
        self.left = None
        self.bottom = None
        self.right = None

        self.top_left = None
        self.top_right = None
        self.bottom_left = None
        self.bottom_right = None

        self.title_separator_left = None
        self.title_separator_right = None


class RectangleStyle3D(RectangleStyle):
    def __init__(self):
        light = colors.GRAY
        medium = colors.GRAY_D
        dark = colors.DARK_BLUE
        very_dark = colors.BLACK
        very_light = colors.WHITE
        self.center = GrahicChar(medium, medium, ' ')
        self.top = GrahicChar(light, light, ' ')
        self.left = self.top
        self.bottom = GrahicChar(dark, dark, ' ')
        self.right = self.bottom
        self.top_left = GrahicChar(light, very_light, '\\')
        self.top_right = GrahicChar(light, dark, 243)
        self.bottom_left = GrahicChar(light, dark, 243)
        self.bottom_right = GrahicChar(dark, very_dark, '\\')

        self.title_separator_left = self.top
        self.title_separator_right = self.top


class FinalFantasyClassicStyle(RectangleStyle):
    def __init__(self):
        white = colors.WHITE
        blue = colors.BLUE_D
        self.center = GrahicChar(blue, blue, ' ')
        self.top = GrahicChar(blue, white, libtcod.CHAR_HLINE)
        self.left = GrahicChar(blue, white, libtcod.CHAR_VLINE)
        self.bottom = self.top
        self.right = self.left
        self.top_left = GrahicChar(blue, white, libtcod.CHAR_DIAMOND)
        self.top_right = self.top_left
        self.bottom_left = self.top_left
        self.bottom_right = self.top_left

        self.title_separator_left = self.top
        self.title_separator_right = self.top


class MinimalClassicStyle(RectangleStyle):
    def __init__(self):
        bg = colors.INTERFACE_BG
        fg = colors.INTERFACE_FG
        self.center = GrahicChar(bg, bg, ' ')
        self.top = GrahicChar(bg, fg, libtcod.CHAR_DHLINE)
        self.left = GrahicChar(bg, fg, libtcod.CHAR_DVLINE)
        self.bottom = self.top
        self.right = self.left
        self.top_left = GrahicChar(bg, fg, libtcod.CHAR_DNW)
        self.top_right = GrahicChar(bg, fg, libtcod.CHAR_DNE)
        self.bottom_left = GrahicChar(bg, fg, libtcod.CHAR_DSW)
        self.bottom_right = GrahicChar(bg, fg, libtcod.CHAR_DSE)

        self.title_separator_left = GrahicChar(bg, fg, 181)
        self.title_separator_right = GrahicChar(bg, fg, 198)


class MinimalClassicStyle2(RectangleStyle):
    def __init__(self):
        bg = colors.INTERFACE_BG
        fg = colors.INTERFACE_FG
        self.center = GrahicChar(bg, bg, ' ')
        self.top = GrahicChar(bg, fg, libtcod.CHAR_DHLINE)
        self.left = GrahicChar(bg, fg, libtcod.CHAR_VLINE)
        self.bottom = self.top
        self.right = self.left
        self.top_left = GrahicChar(bg, fg, 213)
        self.top_right = GrahicChar(bg, fg, 184)
        self.bottom_left = GrahicChar(bg, fg, 212)
        self.bottom_right = GrahicChar(bg, fg, 190)

        self.title_separator_left = GrahicChar(bg, fg, 181)
        self.title_separator_right = GrahicChar(bg, fg, 198)


class MinimalTopCard(RectangleStyle):
    def __init__(self):
        bg = colors.INTERFACE_BG
        fg = colors.INTERFACE_FG
        self.center = GrahicChar(bg, bg, ' ')
        self.top = GrahicChar(bg, fg, libtcod.CHAR_DHLINE)
        self.left = GrahicChar(bg, fg, libtcod.CHAR_VLINE)
        self.bottom = self.center
        self.right = self.left
        self.top_left = GrahicChar(bg, fg, 213)
        self.top_right = GrahicChar(bg, fg, 184)
        self.bottom_left = self.left
        self.bottom_right = self.right

        self.title_separator_left = GrahicChar(bg, fg, 181)
        self.title_separator_right = GrahicChar(bg, fg, 198)


class ChestStyle(RectangleStyle):
    def __init__(self):
        light = colors.RED_D
        dark = colors.DARK_BROWN
        self.center = GrahicChar(dark, light, icon.BIG_CENTER_DOT)
        self.top = GrahicChar(light, dark, libtcod.CHAR_SUBP_N)
        self.left = GrahicChar(dark, light, libtcod.CHAR_SUBP_E)
        self.bottom = GrahicChar(dark, light, libtcod.CHAR_SUBP_N)
        self.right = GrahicChar(light, dark, libtcod.CHAR_SUBP_E)
        self.top_left = GrahicChar(light, dark, libtcod.CHAR_NW)
        self.top_right = GrahicChar(light, dark, libtcod.CHAR_NE)
        self.bottom_left = GrahicChar(light, dark, libtcod.CHAR_SW)
        self.bottom_right = GrahicChar(light, dark, libtcod.CHAR_SE)

        self.title_separator_left = self.top
        self.title_separator_right = self.top


class MinimalStyle(RectangleStyle):
    def __init__(self):
        bg = colors.INTERFACE_BG
        fg = colors.INTERFACE_FG
        self.center = GrahicChar(bg, bg, ' ')
        self.top = GrahicChar(bg, fg, ' ')
        self.left = GrahicChar(bg, fg, ' ')
        self.bottom = self.top
        self.right = self.left
        self.top_left = GrahicChar(bg, fg, libtcod.CHAR_NW)
        self.top_right = GrahicChar(bg, fg, libtcod.CHAR_NE)
        self.bottom_left = GrahicChar(bg, fg, libtcod.CHAR_SW)
        self.bottom_right = GrahicChar(bg, fg, libtcod.CHAR_SE)

        self.title_separator_left = self.top
        self.title_separator_right = self.top

ff_blue_theme = MenuStyle(FinalFantasyClassicStyle(),
                          colors.GRAY, (2, 2))
tlr_classic_3d_theme = MenuStyle(RectangleStyle3D(),
                                 colors.GRAY, (2, 2))
rogue_classic_theme = MenuStyle(MinimalClassicStyle2(),
                                colors.GRAY, (2, 2))

monster_list_card = MinimalTopCard()

themes = {"ff_blue_theme": ff_blue_theme,
          "rogue_classic_theme": rogue_classic_theme,
          "tlr_classic_3d_theme": tlr_classic_3d_theme}

menu_theme = themes[settings.menu_theme]
interface_theme = themes[settings.interface_theme]
