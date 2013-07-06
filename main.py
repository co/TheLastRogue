#!/usr/bin/python

import init
import vector2d
import logging
import gamestate
import menu
import settings

logging.basicConfig(filename="debug.log", level=logging.DEBUG, filemode="w")
init.init_libtcod()

main_menu = menu.MainMenu(vector2d.ZERO, settings.WINDOW_WIDTH,
                          settings.WINDOW_HEIGHT)
gamestate.game_state_stack.push(main_menu)
gamestate.game_state_stack.main_loop()
