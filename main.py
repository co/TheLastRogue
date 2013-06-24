#!/usr/bin/python

'''
libtcod python tutorial
This code modifies samples_py.py from libtcod 1.4.1. It shows a '@'
walking around with a source of light giving simple FOV.
It's in the public domain.
'''

#############################################
# imports
#############################################


import libtcodpy as libtcod
import DungeonLevel as dungeonLevel
import Init as init
import Player as player
import Monster as monster
import Vector2D as vector2D
import Item as item
import Screen as screen
import Camera as camera
import turn
import Settings
import Constants
import Colors
import logging


#############################################
# global constants and variables
#############################################

logging.basicConfig(filename="debug.log", level=logging.DEBUG, filemode="w")
init.init_libtcod()

dungeon_level = dungeonLevel.test_dungeon_level()
camera = camera.Camera(vector2D.Vector2D(Constants.MONSTER_STATUS_BAR_WIDTH,
                                         0),
                       vector2D.Vector2D(0, 0))

hero = player.Player()
start_position = vector2D.Vector2D(20, 10)
hero.try_move_to_position(dungeon_level, start_position)
fov_recompute = True
fov_radius = 4

rat = monster.RatMan()
rat_pos = vector2D.Vector2D(15, 15)
rat.try_move_to_position(dungeon_level, rat_pos)

gun = item.Gun()
item_position = vector2D.Vector2D(20, 20)

gun.try_move_to_position(dungeon_level, item_position)

status_bar = screen.Screen(vector2D.Vector2D(Settings.WINDOW_WIDTH -
                                             Constants.STATUS_BAR_WIDTH, 0),
                           Constants.STATUS_BAR_WIDTH,
                           Constants.STATUS_BAR_HEIGHT,
                           Colors.DB_BLACK)

monster_status_bar =\
    screen.EntityStatusList(vector2D.Vector2D(0, 0),
                            Constants.MONSTER_STATUS_BAR_WIDTH,
                            Constants.MONSTER_STATUS_BAR_HEIGHT,
                            Colors.DB_BLACK)

hp_bar = screen.CounterBar(hero.hp, Constants.STATUS_BAR_WIDTH - 2,
                           Colors.DB_BROWN, Colors.DB_LOULOU)
text_box = screen.TextBox("CO\nThe Brave", vector2D.Vector2D(0, 0),
                          Constants.STATUS_BAR_WIDTH - 2,
                          1, Colors.DB_PANCHO)

status_bar.elements.append(text_box)
status_bar.elements.append(hp_bar)

message_bar = screen.\
    MessageDisplay(vector2D.Vector2D(Constants.MONSTER_STATUS_BAR_WIDTH,
                                     Constants.LEVEL_HEIGHT),
                   Constants.MESSAGES_BAR_WIDTH,
                   Constants.MESSAGES_BAR_HEIGHT,
                   Colors.DB_BLACK)

#############################################
# drawing
#############################################


def draw(camera):
    status_bar.draw()
    message_bar.draw()
    dungeon_level.draw(hero, camera)
    hero.draw(True, camera)
    monster_status_bar.draw()

#############################################
# game state update
#############################################


def update():
    dungeon_level.update(hero)
    monster_status_bar.update(hero)
    message_bar.update()

#############################################
# main loop
#############################################


def main_loop():
    global turn
    while not libtcod.console_is_window_closed():
        turn.current_turn = turn.current_turn + 1
        draw(camera)
        libtcod.console_flush()
        update()
        if(hero.is_dead()):
            break

main_loop()
