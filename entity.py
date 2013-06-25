import random
import counter
import gamepiece
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


class Entity(gamepiece.GamePiece):
    def __init__(self):
        super(Entity, self).__init__()
        self.hp = counter.Counter(1, 1)
        self.fov_map = None
        self._sight_radius = 10

        self.piece_type = gamepiece.ENTITY_GAME_PIECE
        self.max_instances_in_single_tile = 1
        self.draw_order = 0

    def update(self, dungeon_level, player):
        pass

    def step_random_direction(self, dungeon_level):
        direction = random.sample(list(directions.values()), 1)
        new_position = self.position + direction[0]
        self.try_move_to_position(dungeon_level, new_position)

    def try_move_to_position(self, new_dungeon_level, new_position):
        old_dungeon_level = self.dungeon_level
        move_succeded = super(Entity, self).\
            try_move_to_position(new_dungeon_level, new_position)
        if(move_succeded):
            if(not old_dungeon_level is None and
               (not old_dungeon_level is new_dungeon_level)):
                old_dungeon_level.remove_entity_if_present(self)
            new_dungeon_level.add_entity_if_not_present(self)
        return move_succeded

    def try_remove_from_dungeon(self):
        old_dungeon_level = self.dungeon_level
        remove_succeded = super(Entity, self).\
            try_remove_from_dungeon()
        if(remove_succeded and (not old_dungeon_level is None)):
            old_dungeon_level.remove_entity_if_present(self)
        return remove_succeded

    def update_fov_map(self):
        libtcod.map_compute_fov(self.fov_map,
                                self.position.x,
                                self.position.y,
                                self._sight_radius, True)

    def get_seen_entities(self):
        self.update_fov_map()
        seen_entities = []
        for y, row in enumerate(self.dungeon_level.tile_matrix):
            for x, current_tile in enumerate(row):
                entity = current_tile.get_first_entity()
                if(not entity is None and
                   libtcod.map_is_in_fov(self.fov_map, x, y)):
                    seen_entities.append(entity)
        seen_entities.remove(self)
        return seen_entities

    def hurt(self, damage):
        self.hp.decrease(damage)

    def heal(self, health):
        self.hp.increase(health)

    def is_dead(self):
        return self.hp.value == 0

    def kill(self):
        self.hp.set_min()
