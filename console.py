import colors
import frame
import settings
import libtcodpy as libtcod


class ConsoleVisual(object):
    def __init__(self, width, height):
        self._visual_char_matrix =\
            [[GrahicChar(colors.BLACK, colors.BLACK, ' ')
              for _ in range(width)]
             for _ in range(height)]
        self._default_color_fg = colors.BLACK
        self._default_color_bg = colors.BLACK

    def get_color_fg(self, position):
        x, y = position
        return self._visual_char_matrix[y][x].color_fg

    def get_color_bg(self, position):
        x, y = position
        return self._visual_char_matrix[y][x].color_bg

    def get_symbol(self, position):
        x, y = position
        return self._visual_char_matrix[y][x].icon

    def get_default_color_fg(self):
        return self._default_color_fg

    def get_default_color_bg(self):
        return self._default_color_bg

    def set_default_color_fg(self, color):
        if not color == self.get_default_color_fg():
            self._default_color_fg = color
            libtcod.console_set_default_foreground(None, color)

    def set_default_color_bg(self, color):
        if not color == self.get_default_color_bg():
            self._default_color_bg = color
            libtcod.console_set_default_background(None, color)

    def set_symbol(self, position, icon):
        if not icon == self.get_symbol(position):
            x, y = position
            self._visual_char_matrix[y][x].icon = icon
            libtcod.console_set_char(0, x, y, icon)

    def set_color_fg(self, position, color):
        if not color == self.get_color_fg(position):
            x, y = position
            self._visual_char_matrix[y][x].color_fg = color
            libtcod.console_set_char_foreground(0, x, y, color)

    def set_color_bg(self, position, color, effect=libtcod.BKGND_SET):
        if not color == self.get_color_bg(position):
            x, y = position
            self._visual_char_matrix[y][x].color_bg = color
            libtcod.console_set_char_background(0, x, y, color, effect)

    def print_text(self, position, text):
        for idx, char in enumerate(text):
            self.set_color_fg((position[0] + idx, position[1]),
                              self.get_default_color_fg())
            self.set_symbol((position[0] + idx, position[1]), char)

    def print_text_vertical(self, position, text):
        for idx, char in enumerate(text):
            self.set_color_fg((position[0], position[1] + idx),
                              self.get_default_color_fg())
            self.set_symbol((position[0], position[1] + idx), char)

    def set_colors_and_symbol(self, position, color_fg, color_bg, icon):
        if(color_fg == self.get_color_fg(position) and
           color_bg == self.get_color_bg(position) and
           icon == self.get_symbol(position)):
            return
        else:
            x, y = position
            self._visual_char_matrix[y][x].icon = icon
            self._visual_char_matrix[y][x].color_fg = color_fg
            self._visual_char_matrix[y][x].color_bg = color_bg
            libtcod.console_put_char_ex(0, x, y, icon, color_fg, color_bg)

    def flush(self):
        libtcod.console_flush()
        frame.current_frame += 1

    def print_screen(self):
        libtcod.sys_save_screenshot()


class GrahicChar(object):
    """
    Composites holding this has a graphical representation as a char.
    """
    def __init__(self, color_bg, color_fg, icon):
        super(GrahicChar, self).__init__()
        self.icon = icon
        self.color_bg = color_bg
        self.color_fg = color_fg

console = ConsoleVisual(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
