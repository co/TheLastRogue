from graphic import GraphicChar
import icon
import colors
import libtcodpy as libtcod
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

        self.mid_vertical = self.left
        self.mid_horizontal = self.top

        self.top_cross = GraphicChar(bg, fg, " ")
        self.left_cross = GraphicChar(bg, fg, " ")
        self.bottom_cross = GraphicChar(bg, fg, " ")
        self.right_cross = GraphicChar(bg, fg, " ")

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
        self.center = GraphicChar(medium, medium, ' ')
        self.top = GraphicChar(light, light, ' ')
        self.left = self.top
        self.bottom = GraphicChar(dark, dark, ' ')
        self.right = self.bottom

        self.mid_vertical = self.left
        self.mid_horizontal = self.top
        self.mid_cross = self.top

        self.top_left = GraphicChar(light, very_light, '\\')
        self.top_right = GraphicChar(light, dark, 243)
        self.bottom_left = GraphicChar(light, dark, 243)
        self.bottom_right = GraphicChar(dark, very_dark, '\\')

        self.top_cross = GraphicChar(medium, medium, " ")
        self.left_cross = GraphicChar(medium, medium, " ")
        self.bottom_cross = GraphicChar(medium, medium, " ")
        self.right_cross = GraphicChar(medium, medium, " ")

        self.title_separator_left = self.top
        self.title_separator_right = self.top


class FinalFantasyClassicStyle(RectangleStyle):
    def __init__(self, color_fg=colors.WHITE, color_bg=colors.BLUE_D):
        self.center = GraphicChar(color_bg, color_bg, ' ')
        self.top = GraphicChar(color_bg, color_fg, libtcod.CHAR_HLINE)
        self.left = GraphicChar(color_bg, color_fg, libtcod.CHAR_VLINE)
        self.bottom = self.top
        self.right = self.left

        cross = GraphicChar(color_bg, color_fg, libtcod.CHAR_DIAMOND)

        self.mid_vertical = self.left
        self.mid_horizontal = self.top
        self.mid_cross = cross

        self.top_cross = cross
        self.left_cross = cross
        self.bottom_cross = cross
        self.right_cross = cross

        self.top_left = cross
        self.top_right = cross
        self.bottom_left = cross
        self.bottom_right = cross

        self.title_separator_left = self.top
        self.title_separator_right = self.top


class MinimalClassicStyle(RectangleStyle):
    def __init__(self):
        bg = colors.INTERFACE_BG
        fg = colors.INTERFACE_FG
        self.center = GraphicChar(bg, bg, ' ')
        self.top = GraphicChar(bg, fg, libtcod.CHAR_DHLINE)
        self.left = GraphicChar(bg, fg, libtcod.CHAR_DVLINE)
        self.bottom = self.top
        self.right = self.left

        self.mid_vertical = self.left
        self.mid_horizontal = self.top
        self.mid_cross = GraphicChar(bg, fg, libtcod.CHAR_DTEES)

        self.top_cross = GraphicChar(bg, fg, libtcod.CHAR_DTEES)
        self.left_cross = GraphicChar(bg, fg, libtcod.CHAR_DTEEE)
        self.bottom_cross = GraphicChar(bg, fg, libtcod.CHAR_DTEEN)
        self.right_cross = GraphicChar(bg, fg, libtcod.CHAR_DTEEW)

        self.top_left = GraphicChar(bg, fg, libtcod.CHAR_DNW)
        self.top_right = GraphicChar(bg, fg, libtcod.CHAR_DNE)
        self.bottom_left = GraphicChar(bg, fg, libtcod.CHAR_DSW)
        self.bottom_right = GraphicChar(bg, fg, libtcod.CHAR_DSE)

        self.title_separator_left = GraphicChar(bg, fg, 181)
        self.title_separator_right = GraphicChar(bg, fg, 198)

class MinimalClassicStyle2(RectangleStyle):
    def __init__(self):
        bg = colors.INTERFACE_BG
        fg = colors.INTERFACE_FG
        self.center = GraphicChar(bg, bg, ' ')
        self.top = GraphicChar(bg, fg, libtcod.CHAR_DHLINE)
        self.left = GraphicChar(bg, fg, libtcod.CHAR_VLINE)
        self.bottom = self.top
        self.right = self.left

        self.mid_vertical = self.left
        self.mid_horizontal = self.top

        self.top_cross = GraphicChar(bg, fg, libtcod.CHAR_DTEES)
        self.left_cross = GraphicChar(bg, fg, libtcod.CHAR_TEEE)
        self.bottom_cross = GraphicChar(bg, fg, libtcod.CHAR_DTEEN)
        self.right_cross = GraphicChar(bg, fg, libtcod.CHAR_TEEW)

        self.top_left = GraphicChar(bg, fg, 213)
        self.top_right = GraphicChar(bg, fg, 184)
        self.bottom_left = GraphicChar(bg, fg, 212)
        self.bottom_right = GraphicChar(bg, fg, 190)

        self.title_separator_left = GraphicChar(bg, fg, 181)
        self.title_separator_right = GraphicChar(bg, fg, 198)


class MinimalTopCard(RectangleStyle):
    def __init__(self):
        bg = colors.INTERFACE_BG
        fg = colors.INTERFACE_FG
        self.center = GraphicChar(bg, bg, ' ')
        self.top = GraphicChar(bg, fg, libtcod.CHAR_DHLINE)
        self.left = GraphicChar(bg, fg, libtcod.CHAR_VLINE)
        self.bottom = self.center
        self.right = self.left

        self.mid_vertical = self.left
        self.mid_horizontal = self.top

        self.top_left = GraphicChar(bg, fg, 213)
        self.top_right = GraphicChar(bg, fg, 184)
        self.bottom_left = self.left
        self.bottom_right = self.right

        self.top_cross = GraphicChar(bg, fg, libtcod.CHAR_DTEES)
        self.left_cross = GraphicChar(bg, fg, libtcod.CHAR_TEEE)
        self.bottom_cross = GraphicChar(bg, fg, libtcod.CHAR_DTEEN)
        self.right_cross = GraphicChar(bg, fg, libtcod.CHAR_TEEW)

        self.title_separator_left = GraphicChar(bg, fg, 181)
        self.title_separator_right = GraphicChar(bg, fg, 198)


class ChestStyle(RectangleStyle):
    def __init__(self):
        self.light = colors.ORANGE_D
        self.dark = colors.DARK_BROWN
        self.center = GraphicChar(self.dark, self.light, icon.BIG_CENTER_DOT)
        self.top = GraphicChar(self.light, self.dark, libtcod.CHAR_SUBP_N)
        self.left = GraphicChar(self.dark, self.light, libtcod.CHAR_SUBP_E)
        self.bottom = GraphicChar(self.dark, self.light, libtcod.CHAR_SUBP_N)
        self.right = GraphicChar(self.light, self.dark, libtcod.CHAR_SUBP_E)

        self.mid_vertical = self.left
        self.mid_horizontal = self.top

        self.top_left = GraphicChar(self.light, self.dark, libtcod.CHAR_NW)
        self.top_right = GraphicChar(self.light, self.dark, libtcod.CHAR_NE)
        self.bottom_left = GraphicChar(self.light, self.dark, libtcod.CHAR_SW)
        self.bottom_right = GraphicChar(self.light, self.dark, libtcod.CHAR_SE)

        self.top_cross = GraphicChar(self.dark, self.light, " ")
        self.left_cross = GraphicChar(self.dark, self.light, " ")
        self.bottom_cross = GraphicChar(self.dark, self.light, " ")
        self.right_cross = GraphicChar(self.dark, self.light, " ")

        self.title_separator_left = self.top
        self.title_separator_right = self.top


class MinimalChestStyle(ChestStyle):
    def __init__(self):
        super(MinimalChestStyle, self).__init__()
        self.center = GraphicChar(self.dark, self.light, " ")


class MinimalStyle(RectangleStyle):
    def __init__(self):
        bg = colors.INTERFACE_BG
        fg = colors.INTERFACE_FG
        self.center = GraphicChar(bg, bg, ' ')
        self.top = GraphicChar(bg, fg, ' ')
        self.left = GraphicChar(bg, fg, ' ')
        self.bottom = self.top
        self.right = self.left

        self.mid_vertical = self.left
        self.mid_horizontal = self.top

        self.top_left = GraphicChar(bg, fg, libtcod.CHAR_NW)
        self.top_right = GraphicChar(bg, fg, libtcod.CHAR_NE)
        self.bottom_left = GraphicChar(bg, fg, libtcod.CHAR_SW)
        self.bottom_right = GraphicChar(bg, fg, libtcod.CHAR_SE)

        self.top_cross = GraphicChar(bg, fg, " ")
        self.left_cross = GraphicChar(bg, fg, " ")
        self.bottom_cross = GraphicChar(bg, fg, " ")
        self.right_cross = GraphicChar(bg, fg, " ")

        self.title_separator_left = self.top
        self.title_separator_right = self.top

ff_blue_theme = MenuStyle(FinalFantasyClassicStyle(),
                          colors.GRAY, (2, 2))

ff_gold_theme = MenuStyle(FinalFantasyClassicStyle(colors.CHAMPAGNE, colors.DARK_BROWN),
                          colors.GRAY, (2, 2))

ff_red_theme = MenuStyle(FinalFantasyClassicStyle(colors.CHAMPAGNE, colors.RED_D),
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
sacrifice_menu_theme = ff_red_theme
interface_theme = themes[settings.interface_theme]
