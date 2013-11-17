import time
import libtcodpy as libtcod

NORTH = 0
SOUTH = 1
WEST = 2
EAST = 3
NORTHWEST = 4
NORTHEAST = 5
SOUTHWEST = 6
SOUTHEAST = 7
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

controls = {
    't': NORTH,  # up
    libtcod.KEY_UP: NORTH,  # up
    libtcod.KEY_KP8: NORTH,  # up

    'h': SOUTH,   # down
    libtcod.KEY_DOWN: SOUTH,  # up
    libtcod.KEY_KP2: SOUTH,  # up

    'd': WEST,  # left
    libtcod.KEY_LEFT: WEST,  # left
    libtcod.KEY_KP4: WEST,  # up

    'n': EAST,   # right
    libtcod.KEY_RIGHT: EAST,  # right
    libtcod.KEY_KP6: EAST,  # up

    'g': NORTHWEST,   # up, left
    libtcod.KEY_KP7: NORTHWEST,  # up, left

    'c': NORTHEAST,   # up, right
    libtcod.KEY_KP9: NORTHEAST,  # up, right

    'm': SOUTHWEST,   # down, left
    libtcod.KEY_KP1: SOUTHWEST,  # down, left

    'w': SOUTHEAST,   # down, right
    libtcod.KEY_KP3: SOUTHEAST,  # down, right

    'f': FIRE,
    's': STONE,
    '@': PRINTSCREEN,

    libtcod.KEY_ENTER: ENTER,
    libtcod.KEY_ESCAPE: ESCAPE,
    libtcod.KEY_SHIFT: SHIFT,  # shift

    "r": REST,
    ".": REST,
    "p": PICKUP,
    "i": INVENTORY,
    "x": EXAMINE,
    ">": DESCEND,
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


