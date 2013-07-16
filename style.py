import colors


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


class RectangleStyle3D(object):
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
