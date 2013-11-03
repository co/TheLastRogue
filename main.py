#!/usr/bin/python
import cProfile
import init
import logging
import statestack
import menufactory

logging.basicConfig(filename="debug.log", level=logging.DEBUG, filemode="w")
init.init_libtcod()

main_state_stack = statestack.StateStack()
main_menu = menufactory.title_screen(main_state_stack)
main_state_stack.push(main_menu)
main_state_stack.main_loop()
#cProfile.run(main_state_stack.main_loop())
