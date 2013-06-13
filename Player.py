import Counter as counter
import libtcodpy as libtcod

# TODO move to settings.
move_controls = {
    't': (0, -1),  # up
    'h': (0, 1),   # down
    'd': (-1, 0),  # left
    'n': (1, 0),   # right
    libtcod.KEY_UP: (0, -1),  # example of alternate key
    libtcod.KEY_KP8: (0, -1)  # example of alternate key
}


def get_key(key):
    if key.vk == libtcod.KEY_CHAR:
        return chr(key.c)
    else:
        return key.vk


class Player(object):

    def __init__(self, position):
        self.hp = counter.Counter(10, 10)
        self.position = position

    def draw(self):
        libtcod.console_put_char(0, self.position.x, self.position.y,
                                 '@', libtcod.BKGND_NONE)

    def update(self, dungeonLevel):
        key = libtcod.console_wait_for_keypress(True)
        key = get_key(key)
        if key in move_controls:
            dx, dy = move_controls[key]
            if dungeonLevel.isTilePassable(self.position + (dx, dy)):
                self.position = self.position + (dx, dy)
