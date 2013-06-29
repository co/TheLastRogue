import random
import vector2d
import counter
import gamepiece
import entityeffect
import libtcodpy as libtcod

FACTION_PLAYER = 0
FACTION_MONSTER = 1

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
        self._sight_radius = 10
        self._strength = 3
        self._faction = FACTION_MONSTER
        self.effect_queue = entityeffect.EffectQueue()

        self.piece_type = gamepiece.ENTITY_GAME_PIECE
        self.max_instances_in_single_tile = 1
        self.draw_order = 0
        self.dungeon_map = None
        self.path = None
        self.__dungeon_level = None

    @property
    def dungeon_level(self):
        return self.__dungeon_level

    @dungeon_level.setter
    def dungeon_level(self, value):
        if((not self.dungeon_level is value) and (not value is None)):
            self.__dungeon_level = value
            self.update_dungeon_map()
            self.dungeon_map = libtcod.map_new(self.dungeon_level.width,
                                               self.dungeon_level.height)
            self.path = libtcod.path_new_using_map(self.dungeon_map, 1.0)

    def update(self, player):
        pass

    def step_random_direction(self):
        direction = random.sample(list(directions.values()), 1)
        new_position = self.position + direction[0]
        self.try_move(new_position, self.dungeon_level)

    def try_move(self, new_position, new_dungeon_level=None):
        if(new_dungeon_level is None):
            new_dungeon_level = self.dungeon_level
        old_dungeon_level = self.dungeon_level
        move_succeded = super(Entity, self).\
            try_move(new_position, new_dungeon_level)
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

    def get_seen_entities(self):
        seen_entities = []
        for entity in self.dungeon_level.entities:
            if libtcod.map_is_in_fov(self.dungeon_map, entity.position.x,
                                     entity.position.y):
                seen_entities.append(entity)
        return [entity for entity in seen_entities if not entity is self]

    def hurt(self, damage, entity=None):
        self.hp.decrease(damage)
        if(self.is_dead):
            self.killer = entity

    def heal(self, health):
        self.hp.increase(health)

    def is_dead(self):
        return self.hp.value == 0

    def kill(self):
        self.hp.set_min()

    def try_hit(self, position):
        entity = self.dungeon_level.get_tile(position).get_first_entity()
        if(entity is None or
           entity._faction == self._faction):
            return False
        self.hit(entity)
        return True

    def hit(self, target_entity):
        damage = random.randrange(1, self._strength)
        damage_effect = entityeffect.Damage(self, target_entity,
                                            [entityeffect.PHYSICAL], damage)
        target_entity.effect_queue.add(damage_effect)

    def update_effect_queue(self):
        self.effect_queue.update()

    def update_dungeon_map(self):
        for y in range(self.dungeon_level.height):
            for x in range(self.dungeon_level.width):
                terrain = self.dungeon_level.tile_matrix[y][x].terrain
                libtcod.map_set_properties(self.dungeon_map, x, y,
                                           terrain.is_transparent(),
                                           not terrain.is_solid())
        libtcod.map_compute_fov(self.dungeon_map,
                                self.position.x,
                                self.position.y,
                                self._sight_radius, True)

    def has_path(self):
        if(self.path is None or libtcod.path_is_empty(self.path)):
            return False
        return True

    def print_walkable_map(self):
        for y in range(libtcod.map_get_height(self.dungeon_map)):
            line = ""
            for x in range(libtcod.map_get_width(self.dungeon_map)):
                if(libtcod.map_is_walkable(self.dungeon_map, x, y)):
                    line += " "
                else:
                    line += "#"
            print(line)

    def try_step_path(self):
        if(not self.has_path()):
            return False
        x, y = libtcod.path_walk(self.path, True)
        step_succeeded = self.try_move(vector2d.Vector2D(x, y))
        return step_succeeded
