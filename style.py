import colors
import geometry as geo
import libtcodpy as libtcod


class MenuStyle(object):
    def __init__(self, rect_style, inactive_text_color, margin):
        self.rect_style = rect_style
        self.inactive_text_color = inactive_text_color
        self.margin = margin


class CharacterVisual(object):
    def __init__(self, symbol, color_bg, color_fg):
        self.symbol = symbol
        self.color_bg = color_bg
        self.color_fg = color_fg


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


class RectangleStyle3D(RectangleStyle):
    def __init__(self):
        light = colors.DB_TOPAZ
        medium = colors.DB_DIM_GRAY
        dark = colors.DB_SMOKEY_ASH
        very_dark = colors.DB_VALHALLA
        very_light = colors.DB_HEATHER
        self.center = CharacterVisual(' ', medium, medium)
        self.top = CharacterVisual(' ', light, light)
        self.left = self.top
        self.bottom = CharacterVisual(' ', dark, dark)
        self.right = self.bottom
        self.top_left = CharacterVisual('\\', light, very_light)
        self.top_right = CharacterVisual(243, light, dark)
        self.bottom_left = CharacterVisual(243, light, dark)
        self.bottom_right = CharacterVisual('\\', dark, very_dark)


class FinalFantasyClassicStyle(RectangleStyle):
    def __init__(self):
        white = colors.DB_WHITE
        blue = colors.DB_VENICE_BLUE
        self.center = CharacterVisual(' ', blue, blue)
        self.top = CharacterVisual(libtcod.CHAR_HLINE, blue, white)
        self.left = CharacterVisual(libtcod.CHAR_VLINE, blue, white)
        self.bottom = self.top
        self.right = self.left
        self.top_left = CharacterVisual(libtcod.CHAR_DIAMOND, blue, white)
        self.top_right = self.top_left
        self.bottom_left = self.top_left
        self.bottom_right = self.top_left


class MinimalClassicStyle(RectangleStyle):
    def __init__(self):
        bg = colors.DB_VALHALLA
        fg = colors.DB_VENICE_BLUE
        self.center = CharacterVisual(' ', bg, bg)
        self.top = CharacterVisual(libtcod.CHAR_DHLINE, bg, fg)
        self.left = CharacterVisual(libtcod.CHAR_DVLINE, bg, fg)
        self.bottom = self.top
        self.right = self.left
        self.top_left = CharacterVisual(libtcod.CHAR_DNW, bg, fg)
        self.top_right = CharacterVisual(libtcod.CHAR_DNE, bg, fg)
        self.bottom_left = CharacterVisual(libtcod.CHAR_DSW, bg, fg)
        self.bottom_right = CharacterVisual(libtcod.CHAR_DSE, bg, fg)

ff_blue_theme = MenuStyle(FinalFantasyClassicStyle(),
                          colors.DB_TOPAZ, geo.Vector2D(2, 2))
tlr_classic_3d_theme = MenuStyle(RectangleStyle3D(),
                                 colors.DB_TOPAZ, geo.Vector2D(2, 2))
rogue_classic_theme = MenuStyle(MinimalClassicStyle(),
                                colors.DB_TOPAZ, geo.Vector2D(2, 2))
