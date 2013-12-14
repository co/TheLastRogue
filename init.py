import os
import settings
import libtcodpy as libtcod


def init_libtcod():
    font = os.path.join('fonts', 'terminal16x16_gs_ro.png')
    libtcod.console_set_custom_font(font,
                                    libtcod.FONT_LAYOUT_ASCII_INROW |
                                    libtcod.FONT_TYPE_GREYSCALE,
                                    16, 32)
    libtcod.console_init_root(settings.SCREEN_WIDTH,
                              settings.SCREEN_HEIGHT,
                              b'The Last Rogue',
                              settings.FULL_SCREEN)
    fps = settings.FPS
    libtcod.sys_set_fps(fps)
