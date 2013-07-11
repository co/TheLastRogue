#!/usr/bin/python

import init
import vector2d
import logging
import statestack
import menu
import settings

logging.basicConfig(filename="debug.log", level=logging.DEBUG, filemode="w")
init.init_libtcod()

main_state_stack = statestack.StateStack()
main_menu = menu.MainMenu(vector2d.ZERO, settings.WINDOW_WIDTH,
                          settings.WINDOW_HEIGHT)
main_state_stack.push(main_menu)
main_state_stack.main_loop()
