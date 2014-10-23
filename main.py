#!/usr/bin/python
#import cProfile
import logging
import gamestate
import init
import statestack
import menufactory


logging.basicConfig(filename="debug.log", level=logging.DEBUG, filemode="w")
init.init_libtcod()

main_state_stack = statestack.StateStack()
main_menu = menufactory.title_screen(main_state_stack, gamestate.GameState, gamestate.TestGameState)
main_state_stack.push(main_menu)
main_state_stack.main_loop()
main_state_stack.main_loop()