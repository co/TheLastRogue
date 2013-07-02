import counter
import monsterspawner
import colors
import dungeonlevel
import entity
import entityeffect
import numpy
import libtcodpy as libtcod


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

    libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS,
                               key, mouse, False)
    key_char = get_key_char(key)
    return key_char


def get_key_char(key):
    if key.vk == libtcod.KEY_CHAR:
        return chr(key.c)
    else:
        return key.vk


class Player(entity.Entity):
    def __init__(self):
        super(Player, self).__init__()
        self.hp = counter.Counter(10, 10)
        self._memory_map = []
        self._faction = entity.FACTION_PLAYER
        self._name = "CO"

    @property
    def color_fg(self):
        if(self.has_status(entity.StatusFlags.INVISIBILE)):
            return colors.DB_VIKING
        return colors.DB_WHITE

    @property
    def symbol(self):
        return ord('@')

    def update(self, _):
        done = False
        while not done:
            key = wait_for_keypress()
            position = self.position
            if key in move_controls:
                dx, dy = move_controls[key]
                new_position = position + (dx, dy)
                move_succeded = self.try_move(new_position)
                done = move_succeded
                if(not done):
                    done = self.try_hit(new_position)
            elif key == libtcod.KEY_ESCAPE:
                self.kill()
                done = True
            elif key == 'r':  # Rest
                done = True
            elif key == 'p':  # Pick up
                done = True
            elif key == 'a':
                self.hurt(1)
                done = True
            elif key == 'o':
                self.heal(1)
            elif key == 'i':
                invisibile_flag = entity.StatusFlags.INVISIBILE
                if(not self.has_status(invisibile_flag)):
                    effect = entityeffect.\
                        StatusAdder(self, self,
                                    invisibile_flag,
                                    time_to_live=numpy.inf)
                    self.add_entity_effect(effect)
                else:
                    invisible_status = entity.StatusFlags.INVISIBILE
                    effect = entityeffect.StatusRemover(self, self,
                                                        invisible_status,
                                                        time_to_live=1)
                    self.add_entity_effect(effect)
                done = True
            elif key == 'm':
                monsterspawner.spawn_rat_man(self.dungeon_level)
                done = True

    def get_memory_of_map(self, dungeon_level):
        self.set_memory_map_if_not_set(dungeon_level)
        return self._memory_map[dungeon_level.depth]

    def set_memory_map_if_not_set(self, dungeon_level):
        depth = dungeon_level.depth
        while(len(self._memory_map) <= depth):
            self._memory_map.append(None)
        if(self._memory_map[depth] is None):
            self._memory_map[depth] = dungeonlevel.unknown_level_map(
                dungeon_level.width, dungeon_level.height, dungeon_level.depth)

    def update_memory_of_tile(self, tile, position, depth):
        self._memory_map[depth].tile_matrix[position.y][position.x]\
            = tile.copy()
