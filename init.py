import constants
import settings
import libtcodpy as libtcod
import os


def init_libtcod():
    font = os.path.join('fonts', 'terminal16x16_gs_ro.png')
    libtcod.console_set_custom_font(font,
                                    libtcod.FONT_LAYOUT_ASCII_INROW |
                                    libtcod.FONT_TYPE_GREYSCALE)
    libtcod.console_init_root(settings.WINDOW_WIDTH,
                              settings.WINDOW_HEIGHT,
                              b'The Last Rogue',
                              False)
    fps = constants.FPS
    libtcod.sys_set_fps(fps)
