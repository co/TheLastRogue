import time
import libtcodpy as libtcod
import settings

NORTH = 0
SOUTH = 1
WEST = 2
EAST = 3
NORTHWEST = 4
NORTHEAST = 5
SOUTHWEST = 6
SOUTHEAST = 7

VI_NORTH = 200
VI_SOUTH = 201
VI_WEST = 202
VI_EAST = 203
VI_NORTHWEST = 204
VI_NORTHEAST = 205
VI_SOUTHWEST = 206
VI_SOUTHEAST = 207

ENTER = 104
REST = 105
ONE = 106
TWO = 107
THREE = 108
FOUR = 109
FIVE = 110
SIX = 111
SEVEN = 112
EIGHT = 113
NINE = 114
ESCAPE = 115
PICKUP = 116
INVENTORY = 117
EXAMINE = 118
SHIFT = 119
DESCEND = 120
ZERO = 121
FIRE = 122
PRINTSCREEN = 123
TAB = 124
STONE = 125
SPACE = 126
DELETE = 127
BACKSPACE = 128
EQUIPMENT = 129


#Aliases:
UP = NORTH
DOWN = SOUTH
LEFT = WEST
RIGHT = EAST

KEY_SHIFT = libtcod.KEY_SHIFT

# TODO move to settings.
move_controls = {
    NORTH: (0, -1),
    SOUTH: (0, 1),
    WEST: (-1, 0),
    EAST: (1, 0),
    NORTHWEST: (-1, -1),
    NORTHEAST: (1, -1),
    SOUTHWEST: (-1, 1),
    SOUTHEAST: (1, 1)
}

vi_move_controls = {
    VI_NORTH: (0, -1),
    VI_SOUTH: (0, 1),
    VI_WEST: (-1, 0),
    VI_EAST: (1, 0),
    VI_NORTHWEST: (-1, -1),
    VI_NORTHEAST: (1, -1),
    VI_SOUTHWEST: (-1, 1),
    VI_SOUTHEAST: (1, 1)
}

controls = {
    settings.KEY_UP: VI_NORTH,  # up
    libtcod.KEY_UP: NORTH,  # up
    libtcod.KEY_KP8: NORTH,  # up

    settings.KEY_DOWN: VI_SOUTH,   # down
    libtcod.KEY_DOWN: SOUTH,  # up
    libtcod.KEY_KP2: SOUTH,  # up

    settings.KEY_LEFT: VI_WEST,  # left
    libtcod.KEY_LEFT: WEST,  # left
    libtcod.KEY_KP4: WEST,  # up

    settings.KEY_RIGHT: VI_EAST,   # right
    libtcod.KEY_RIGHT: EAST,  # right
    libtcod.KEY_KP6: EAST,  # up

    settings.KEY_UP_LEFT: VI_NORTHWEST,   # up, left
    libtcod.KEY_KP7: NORTHWEST,  # up, left

    settings.KEY_UP_RIGHT: VI_NORTHEAST,   # up, right
    libtcod.KEY_KP9: NORTHEAST,  # up, right

    settings.KEY_DOWN_LEFT: VI_SOUTHWEST,   # down, left
    libtcod.KEY_KP1: SOUTHWEST,  # down, left

    settings.KEY_DOWN_RIGHT: VI_SOUTHEAST,   # down, right
    libtcod.KEY_KP3: SOUTHEAST,  # down, right

    settings.KEY_FIRE: FIRE,
    settings.KEY_STONE: STONE,
    libtcod.KEY_F12: PRINTSCREEN,

    libtcod.KEY_ENTER: ENTER,
    libtcod.KEY_ESCAPE: ESCAPE,
    libtcod.KEY_SHIFT: SHIFT,  # shift

    settings.KEY_REST: REST,
    settings.KEY_INVENTORY: INVENTORY,
    settings.KEY_EQUIPMENT: EQUIPMENT,
    settings.KEY_EXAMINE: EXAMINE,
    libtcod.KEY_0: ZERO,
    libtcod.KEY_1: ONE,
    libtcod.KEY_2: TWO,
    libtcod.KEY_3: THREE,
    libtcod.KEY_4: FOUR,
    libtcod.KEY_5: FIVE,
    libtcod.KEY_6: SIX,
    libtcod.KEY_7: SEVEN,
    libtcod.KEY_8: EIGHT,
    libtcod.KEY_9: NINE,
    libtcod.KEY_TAB: TAB,
    libtcod.KEY_SPACE: SPACE,
    libtcod.KEY_DELETE: DELETE,
    libtcod.KEY_BACKSPACE: BACKSPACE,
}


class InputHandler(object):
    def __init__(self):
        self.mouse = libtcod.Mouse()
        self.key = libtcod.Key()

    def update_keys(self):
        libtcod.sys_check_for_event(libtcod.EVENT_ANY, self.key, self.mouse)

    def get_keypress(self):
        key_char = self._get_key_char(self.key)
        if key_char in controls.keys() and self.key.pressed:
            return controls[key_char]
        return None

    def get_keypress_char(self):
        if self.key.pressed:
            return chr(self.key.c)  # Case insensetive
        return None

    def _get_key_char(self, key):
        if key.vk == libtcod.KEY_CHAR:
            return chr(key.c).lower()  # Case insensetive
        else:
            return key.vk

    def is_special_key_pressed(self, special_key):
        if special_key in controls.keys():
            return libtcod.console_is_key_pressed(special_key)
        return False

    def get_mouse_position(self):
        return self.mouse.cx, self.mouse.cy

    def get_left_mouse_press(self):
        return self.mouse.lbutton

handler = InputHandler()


