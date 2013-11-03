import console
import colors
from compositecore import Leaf


class GraphicChar(Leaf):
    """
    Composites holding this has a graphical representation as a char.
    """
    def __init__(self, color_bg, color_fg, symbol):
        super(GraphicChar, self).__init__()
        self.component_type = "graphic_char"
        self._symbol = symbol
        self._color_bg = color_bg
        self._color_fg = color_fg

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, value):
        self._symbol = value

    @property
    def color_bg(self):
        return self._color_bg

    @color_bg.setter
    def color_bg(self, value):
        self._color_bg = value

    @property
    def color_fg(self):
        return self._color_fg

    @color_fg.setter
    def color_fg(self, value):
        self._color_fg = value

    def copy(self):
        """
        Makes a copy of this component.
        """
        return GraphicChar(self.color_bg, self.color_fg, self.symbol)


class CharPrinter(Leaf):
    def __init__(self):
        super(CharPrinter, self).__init__()
        self.component_type = "char_printer"
        self._status_cycle_colors = []
        self._blink_color_fg_queue = []

    def draw_no_effect(self, position):
        """
        Draws the char on the given position on the console.

        Bypasses all effects.
        """
        if(not self.parent.graphic_char.color_bg is None):
            console.console.set_color_bg(position,
                                         self.parent.graphic_char.color_bg)
        if(not self.parent.graphic_char.color_fg is None):
            console.console.set_color_fg(position,
                                         self.parent.graphic_char.color_fg)
        if(not self.parent.graphic_char.symbol is None):
            console.console.set_symbol(position,
                                       self.parent.graphic_char.symbol)

    def draw(self, position):
        """
        Draws the char on the given position on the console.
        """
        self.draw_no_effect(position)
        if(len(self._blink_color_fg_queue) > 0):
            console.console.set_color_fg(position,
                                         self._blink_color_fg_queue.pop())

    def draw_unseen(self, screen_position):
        """
        Draws the char as it looks like outside the field of view.
        """
        console.console.set_colors_and_symbol(screen_position,
                                              colors.UNSEEN_FG,
                                              colors.UNSEEN_BG,
                                              self.parent.graphic_char.symbol)

    def set_fg_blink_colors(self, colors):
        """
        Sets the foreground blink queue.

        These colors will be drawn as an effect,
        the regular colors won't be drawn until the blink queue is empty.
        """
        self._blink_color_fg_queue = colors


class GraphicCharTerrainCorners(GraphicChar):
    """
    Composites holding this has a graphical representation as a char.
    """
    def __init__(self, color_bg, color_fg, symbol, sticky_terrain_classes):
        super(GraphicCharTerrainCorners, self).__init__(color_bg, color_fg,
                                                        symbol)
        self._sticky_terrain_classes = sticky_terrain_classes
        self._wall_symbol_row = symbol
        self.has_calculated = False

    @property
    def symbol(self):
        if not self.has_calculated:
            self.calculate_wall_symbol()
        return self._symbol

    def calculate_wall_symbol(self):
        neighbours_mask = 0
        for index, neighbour in enumerate(self._get_neighbour_terrains()):
            if(any([terrain is neighbour.__class__
                   for terrain in self._sticky_terrain_classes])):
                neighbours_mask |= 2 ** index
        self._symbol = self._wall_symbol_row + neighbours_mask

    def _get_neighbour_terrains(self):
        tiles = (self.parent.dungeon_level.value.
                 get_tiles_surrounding_position(self.parent.position.value))
        return [tile.get_terrain() for tile in tiles]

    def copy(self):
        """
        Makes a copy of this component.
        """
        return GraphicChar(self.color_bg, self.color_fg, self.symbol)
