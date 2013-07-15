#!/usr/bin/python

import init
import geometry as geo
import logging
import statestack
import menu
import settings

logging.basicConfig(filename="debug.log", level=logging.DEBUG, filemode="w")
init.init_libtcod()

main_state_stack = statestack.StateStack()
main_menu_rect = geo.Rect(geo.zero2d(), settings.WINDOW_WIDTH,
                          settings.WINDOW_HEIGHT)
main_menu = menu.MainMenu(main_menu_rect)
main_state_stack.push(main_menu)
main_state_stack.main_loop()
