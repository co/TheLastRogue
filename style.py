import colors
import libtcodpy as libtcod
from console import GFXChar
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
        self.center = GFXChar(' ', medium, medium)
        self.top = GFXChar(' ', light, light)
        self.left = self.top
        self.bottom = GFXChar(' ', dark, dark)
        self.right = self.bottom
        self.top_left = GFXChar('\\', light, very_light)
        self.top_right = GFXChar(243, light, dark)
        self.bottom_left = GFXChar(243, light, dark)
        self.bottom_right = GFXChar('\\', dark, very_dark)

        self.title_separator_left = self.top
        self.title_separator_right = self.top


class FinalFantasyClassicStyle(RectangleStyle):
    def __init__(self):
        white = colors.WHITE
        blue = colors.BLUE_D
        self.center = GFXChar(' ', blue, blue)
        self.top = GFXChar(libtcod.CHAR_HLINE, blue, white)
        self.left = GFXChar(libtcod.CHAR_VLINE, blue, white)
        self.bottom = self.top
        self.right = self.left
        self.top_left = GFXChar(libtcod.CHAR_DIAMOND, blue, white)
        self.top_right = self.top_left
        self.bottom_left = self.top_left
        self.bottom_right = self.top_left

        self.title_separator_left = self.top
        self.title_separator_right = self.top


class MinimalClassicStyle(RectangleStyle):
    def __init__(self):
        bg = colors.INTERFACE_BG
        fg = colors.INTERFACE_FG
        self.center = GFXChar(' ', bg, bg)
        self.top = GFXChar(libtcod.CHAR_DHLINE, bg, fg)
        self.left = GFXChar(libtcod.CHAR_DVLINE, bg, fg)
        self.bottom = self.top
        self.right = self.left
        self.top_left = GFXChar(libtcod.CHAR_DNW, bg, fg)
        self.top_right = GFXChar(libtcod.CHAR_DNE, bg, fg)
        self.bottom_left = GFXChar(libtcod.CHAR_DSW, bg, fg)
        self.bottom_right = GFXChar(libtcod.CHAR_DSE, bg, fg)

        self.title_separator_left = GFXChar(181, bg, fg)
        self.title_separator_right = GFXChar(198, bg, fg)


ff_blue_theme = MenuStyle(FinalFantasyClassicStyle(),
                          colors.GRAY, (2, 2))
tlr_classic_3d_theme = MenuStyle(RectangleStyle3D(),
                                 colors.GRAY, (2, 2))
rogue_classic_theme = MenuStyle(MinimalClassicStyle(),
                                colors.GRAY, (2, 2))

themes = {"ff_blue_theme": ff_blue_theme,
          "rogue_classic_theme": rogue_classic_theme,
          "tlr_classic_3d_theme": tlr_classic_3d_theme}

menu_theme = themes[settings.menu_theme]
interface_theme = themes[settings.interface_theme]
