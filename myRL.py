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
import DungeonLevel
import Init as init
import Player as player
import Vector2D as vector2D


#############################################
# global constants and variables
#############################################

init.init_libtcod()

hero = player.Player(vector2D.Vector2D(20, 10))
fov_recompute = True
fov_radius = 4

dungeonLevel = DungeonLevel.DungeonLevel()

#############################################
# drawing
#############################################


def draw():
    dungeonLevel.Draw(hero.position)
    hero.draw()

#############################################
# game state update
#############################################


def update():
    hero.update(dungeonLevel)


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
