import colors
import frame
import settings
import libtcodpy as libtcod


class ConsoleVisual(object):
    def __init__(self, width, height):
        pass

    def get_color_fg(self, position):
        x, y = position
        return libtcod.console_get_char_foreground(x, y)

    def get_color_bg(self, position):
        x, y = position
        return libtcod.console_get_char_background(x, y)

    def get_symbol(self, position):
        x, y = position
        return libtcod.console_get_char(x, y)

    def get_default_color_fg(self):
        return libtcod.console_get_default_foreground(0)

    def get_default_color_bg(self):
        return libtcod.console_get_default_background(0)

    def set_default_color_fg(self, color, console=0):
        self._default_color_fg = color
        libtcod.console_set_default_foreground(console, color)

    def set_default_color_bg(self, color, console=0):
        self._default_color_bg = color
        libtcod.console_set_default_background(console, color)

    def set_symbol(self, position, icon, console=0):
        x, y = position
        libtcod.console_set_char(console, x, y, icon)

    def set_color_fg(self, position, color, console=0):
        x, y = position
        libtcod.console_set_char_foreground(console, x, y, color)

    def set_color_bg(self, position, color, effect=libtcod.BKGND_SET, console=0):
        x, y = position
        libtcod.console_set_char_background(console, x, y, color, effect)

    def print_text(self, position, text):
        for idx, char in enumerate(text):
            self.set_color_fg((position[0] + idx, position[1]),
                              self.get_default_color_fg())
            self.set_symbol((position[0] + idx, position[1]), char)

    def print_text_vertical(self, position, text):
        for idx, char in enumerate(text):
            self.set_color_fg((position[0], position[1] + idx), self.get_default_color_fg())
            self.set_symbol((position[0], position[1] + idx), char)

    def set_colors_and_symbol(self, position, color_fg, color_bg, icon, console=0):
        x, y = position
        libtcod.console_put_char_ex(console, x, y, icon, color_fg, color_bg)

    def flush(self):
        libtcod.console_flush()
        frame.current_frame += 1

    def print_screen(self):
        libtcod.sys_save_screenshot()

console = ConsoleVisual(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)