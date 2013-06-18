import random
import Counter as counter
import Colors as colors
import libtcodpy as libtcod

directions = {
    "E": (1, 0),
    "N": (0, 1),
    "W": (-1, 0),
    "S": (0, -1),
    "NW": (-1, 1),
    "NE": (1, 1),
    "SW": (-1, -1),
    "SE": (1, -1)
}


class Entity(object):
    def __init__(self, position):
        self.position = position
        self.hp = counter.Counter(1, 1)
        pass

    @staticmethod
    def get_color_fg():
        return colors.UNINITIALIZED_FG

    def is_dead(self):
        return self.hp.value == 0

    def kill(self):
        self.hp.value = 0

    @staticmethod
    def get_symbol():
        return ord('?')

    def draw(self, is_seen):
        if(is_seen):
            fg_color = self.get_color_fg()
        else:
            fg_color = colors.UNSEEN_FG

        libtcod.console_set_char_foreground(0, self.position.x,
                                            self.position.y, fg_color)
        libtcod.console_set_char(0, self.position.x, self.position.y,
                                 self.get_symbol())

    def step_random_direction(self, dungeon_level):
        direction = random.sample(list(directions.values()), 1)
        new_position = self.position + direction[0]
        if(dungeon_level.is_tile_passable(new_position)):
            self.try_move_to_new_position(dungeon_level, new_position)

    def try_move_to_new_position(self, dungeon_level, new_position):
        new_tile = dungeon_level.tile_matrix[new_position.y][new_position.x]
        if((not new_tile.entity is None) or
           new_tile.terrain.is_solid()):
            return False
        self.__move_to_new_position(dungeon_level, new_position)
        return True

    def __move_to_new_position(self, dungeon_level, new_position):
        old_position = self.position
        entity_on_my_position = dungeon_level.\
            tile_matrix[old_position.y][old_position.x].entity
        if(entity_on_my_position is self):
            dungeon_level.\
                tile_matrix[old_position.y][old_position.x].entity = None

        self.position = new_position
        dungeon_level.tile_matrix[new_position.y][new_position.x].entity = self
