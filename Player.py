import Counter as counter
import DungeonLevel as dungeonLevel
import libtcodpy as libtcod
import Entity as entity


# TODO move to settings.
move_controls = {
    't': (0, -1),  # up
    'h': (0, 1),   # down
    'd': (-1, 0),  # left
    'n': (1, 0),   # right
}


def wait_for_keypress():
    key = libtcod.Key()
    mouse = libtcod.Mouse()

    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS,
                                key, mouse)
    key_char = get_key_char(key)
    while not any(key_char == k for k in move_controls.keys()):
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS,
                                    key, mouse)
        key_char = get_key_char(key)
    return key_char


def get_key_char(key):
    if key.vk == libtcod.KEY_CHAR:
        return chr(key.c)
    else:
        return key.vk


class Player(entity.Entity):

    def __init__(self, dungeon_location):
        self.hp = counter.Counter(10, 10)
        self.dungeon_location = dungeon_location
        self.current_depth = 0
        self.fov_map = None
        self._sight_radius = 10
        self._memory_map = []

    def draw(self):
        libtcod.console_put_char(0,
                                 self.dungeon_location.position.x,
                                 self.dungeon_location.position.y,
                                 '@', libtcod.BKGND_NONE)

    def update(self, dungeonLevel):
        key = wait_for_keypress()
        position = self.dungeon_location.position
        if key in move_controls:
            dx, dy = move_controls[key]
            if dungeonLevel.is_tile_passable(position + (dx, dy)):
                self.dungeon_location.position = position + (dx, dy)

    def get_memory_of_map(self, dungeon_level):
        self.set_memory_map_if_not_set(dungeon_level)
        return self._memory_map[dungeon_level.depth]

    def set_memory_map_if_not_set(self, dungeon_level):
        depth = dungeon_level.depth
        while(len(self._memory_map) <= depth):
            self._memory_map.append(None)
        if(self._memory_map[depth] is None):
            self._memory_map[depth] = dungeonLevel.unknown_level_map(
                dungeon_level.width, dungeon_level.height, dungeon_level.depth)

    def update_memory_of_tile(self, tile, x, y, depth):
        self._memory_map[depth].tile_matrix[y][x] = tile

    def update_fov_map(self):
        libtcod.map_compute_fov(self.fov_map,
                                self.dungeon_location.position.x,
                                self.dungeon_location.position.y,
                                self._sight_radius, True)
