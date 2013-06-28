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
import dungeonlevel
import init
import player
import monster
import vector2d
import item
import screen
import camera
import turn
import settings
import constants
import colors
import logging


#############################################
# global constants and variables
#############################################

logging.basicConfig(filename="debug.log", level=logging.DEBUG, filemode="w")
init.init_libtcod()

dungeon_level = dungeonlevel.test_dungeon_level()
camera = camera.Camera(vector2d.Vector2D(constants.MONSTER_STATUS_BAR_WIDTH,
                                         0),
                       vector2d.Vector2D(0, 0))

hero = player.Player()
start_position = vector2d.Vector2D(20, 10)
hero.try_move_to_position(dungeon_level, start_position)

rat = monster.RatMan()
rat_pos = vector2d.Vector2D(15, 15)
rat.try_move_to_position(dungeon_level, rat_pos)

statue = monster.StoneStatue()
statue_pos = vector2d.Vector2D(25, 7)
statue.try_move_to_position(dungeon_level, statue_pos)

gun = item.Gun()
item_position = vector2d.Vector2D(20, 20)

gun.try_move_to_position(dungeon_level, item_position)

status_bar = screen.Screen(vector2d.Vector2D(settings.WINDOW_WIDTH -
                                             constants.STATUS_BAR_WIDTH, 0),
                           constants.STATUS_BAR_WIDTH,
                           constants.STATUS_BAR_HEIGHT,
                           colors.DB_BLACK)

monster_status_bar =\
    screen.EntityStatusList(vector2d.Vector2D(0, 0),
                            constants.MONSTER_STATUS_BAR_WIDTH,
                            constants.MONSTER_STATUS_BAR_HEIGHT,
                            colors.DB_BLACK)

hp_bar = screen.CounterBar(hero.hp, constants.STATUS_BAR_WIDTH - 2,
                           colors.DB_BROWN, colors.DB_LOULOU)
text_box = screen.TextBox("CO\nThe Brave", vector2d.Vector2D(0, 0),
                          constants.STATUS_BAR_WIDTH - 2,
                          1, colors.DB_PANCHO)

status_bar.elements.append(text_box)
status_bar.elements.append(hp_bar)

message_bar = screen.\
    MessageDisplay(vector2d.Vector2D(constants.MONSTER_STATUS_BAR_WIDTH,
                                     constants.LEVEL_HEIGHT),
                   constants.MESSAGES_BAR_WIDTH,
                   constants.MESSAGES_BAR_HEIGHT,
                   colors.DB_BLACK)

#############################################
# drawing
#############################################


def draw(camera):
    status_bar.draw()
    message_bar.draw()
    dungeon_level.draw(hero, camera)
    hero.draw(True, camera)
    monster_status_bar.draw()
    libtcod.console_flush()

#############################################
# game state update
#############################################


def update():
    dungeon_level.update(hero)
    dungeon_level.remove_dead_monsters()
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
        update()
        if(hero.is_dead()):
            break

main_loop()
