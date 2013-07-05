import libtcodpy as libtcod

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3
ENTER = 4

# TODO move to settings.
move_controls = {
    UP: (0, -1),  # up
    DOWN: (0, 1),   # down
    LEFT: (-1, 0),  # left
    RIGHT: (1, 0),   # right
}

controls = {
    't': UP,  # up
    libtcod.KEY_UP: UP,  # up

    'h': DOWN,   # down
    libtcod.KEY_DOWN: DOWN,  # up

    'd': LEFT,  # left
    'n': RIGHT,   # right

    libtcod.KEY_ENTER: ENTER,  # up
}


def wait_for_keypress():
    key = libtcod.Key()
    mouse = libtcod.Mouse()

    libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS,
                               key, mouse, False)
    key_char = get_key_char(key)
    return key_char


def get_keypress():
    key = libtcod.Key()
    mouse = libtcod.Mouse()

    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS,
                                key, mouse)
    key_char = get_key_char(key)
    if key_char in controls.keys():
        return controls[key_char]
    return None


def get_key_char(key):
    if key.vk == libtcod.KEY_CHAR:
        return chr(key.c)
    else:
        return key.vk
