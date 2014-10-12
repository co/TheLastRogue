import os
import settings
import libtcodpy as libtcod

FONT_FILE_PATH = os.path.join('fonts', 'terminal16x16_gs_ro.png')


def init_libtcod():
    libtcod.console_set_custom_font(FONT_FILE_PATH,
                                    libtcod.FONT_LAYOUT_ASCII_INROW |
                                    libtcod.FONT_TYPE_GREYSCALE,
                                    16, 34)
    libtcod.console_init_root(settings.SCREEN_WIDTH,
                              settings.SCREEN_HEIGHT,
                              b'The Last Rogue',
                              settings.FULL_SCREEN)
    fps = settings.FPS
    libtcod.sys_set_fps(fps)
