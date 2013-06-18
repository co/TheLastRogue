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


#############################################
# global constants and variables
#############################################

init.init_libtcod()
start_position = vector2D.Vector2D(20, 10)

hero = player.Player(start_position)
fov_recompute = True
fov_radius = 4


dungeon_level = dungeonLevel.test_dungeon_level()

rat_pos = vector2D.Vector2D(15, 15)
dungeon_level.try_add_monster(monster.RatMan(rat_pos))

gun = item.Gun()
item_position = vector2D.Vector2D(20, 20)

dungeon_level.put_item_on_tile(gun, item_position)

#############################################
# drawing
#############################################


def draw():
    dungeon_level.draw(hero)
    hero.draw(True)

#############################################
# game state update
#############################################


def update():
    hero.update(dungeon_level)
    dungeon_level.update(hero)

#############################################
# main loop
#############################################


def main_loop():
    frame = 0
    while not libtcod.console_is_window_closed():
        frame = frame + 1
        draw()
        libtcod.console_flush()
        update()
        if hero.hp.value == 0:
            break

main_loop()
