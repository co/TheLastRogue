import colors
import frame
import settings
import libtcodpy as libtcod


class CharacterVisual(object):
    def __init__(self, symbol=' ', color_bg=colors.BLACK,
                 color_fg=colors.BLACK):
        self.symbol = symbol
        self.color_bg = color_bg
        self.color_fg = color_fg


class ConsoleVisual(object):
    def __init__(self, width, height):
        self._visual_char_matrix =\
            [[CharacterVisual() for _ in range(width)] for _ in range(height)]
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
        return self._visual_char_matrix[y][x].symbol

    def get_default_color_fg(self):
        return self._default_color_fg

    def get_default_color_bg(self):
        return self._default_color_bg

    def set_default_color_fg(self, color):
        if(not color == self.get_default_color_fg()):
            self._default_color_fg = color
            libtcod.console_set_default_foreground(None, color)

    def set_default_color_bg(self, color):
        if(not color == self.get_default_color_bg()):
            self._default_color_bg = color
            libtcod.console_set_default_background(None, color)

    def set_symbol(self, position, symbol):
        if(not symbol == self.get_symbol(position)):
            x, y = position
            self._visual_char_matrix[y][x].symbol = symbol
            libtcod.console_set_char(0, x, y, symbol)

    def set_color_fg(self, position, color):
        if(not color == self.get_color_fg(position)):
            x, y = position
            self._visual_char_matrix[y][x].color_fg = color
            libtcod.console_set_char_foreground(0, x, y, color)

    def set_color_bg(self, position, color, effect=libtcod.BKGND_SET):
        if(not color == self.get_color_bg(position) or
           not effect == libtcod.BKGND_SET):
            x, y = position
            self._visual_char_matrix[y][x].color_bg = color
            libtcod.console_set_char_background(0, x, y, color, effect)

    def print_text(self, position, text):
        for idx, char in enumerate(text):
            self.set_color_fg((position[0] + idx, position[1]),
                              self.get_default_color_fg())
            self.set_symbol((position[0] + idx, position[1]), char)

    def set_colors_and_symbol(self, position, color_fg, color_bg, symbol):
        if(color_fg == self.get_color_fg(position) and
           color_bg == self.get_color_bg(position) and
           symbol == self.get_symbol(position)):
            return
        else:
            x, y = position
            self._visual_char_matrix[y][x].symbol = symbol
            self._visual_char_matrix[y][x].color_fg = color_fg
            self._visual_char_matrix[y][x].color_bg = color_bg
            libtcod.console_put_char_ex(0, x, y, symbol, color_fg, color_bg)

    def flush(self):
        libtcod.console_flush()
        frame.current_frame += 1

    def print_screen(self):
        libtcod.sys_save_screenshot()


console = ConsoleVisual(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
