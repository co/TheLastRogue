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
import DungeonLocation as dungeonLocation
import Init as init
import Player as player
import Vector2D as vector2D


#############################################
# global constants and variables
#############################################

init.init_libtcod()
start_position = vector2D.Vector2D(20, 10)
start_depth = 0
hero_start_position = dungeonLocation.DungeonLocation(start_depth,
                                                      start_position)

hero = player.Player(hero_start_position)
fov_recompute = True
fov_radius = 4

dungeon_level = dungeonLevel.test_dungeon_level()

#############################################
# drawing
#############################################


def draw():
    dungeon_level.draw(hero)
    hero.draw()

#############################################
# game state update
#############################################


def update():
    hero.update(dungeon_level)


#############################################
# main loop
#############################################

frame = 0
while not libtcod.console_is_window_closed():
    print(frame)
    frame = frame + 1
    draw()
    libtcod.console_flush()
    update()
    if hero.hp.value == 0:
        break
