import random
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
        self.fov_map = None
        self._sight_radius = 10
        self._strength = 3
        self._faction = FACTION_MONSTER
        self.effect_queue = entityeffect.EffectQueue()

        self.piece_type = gamepiece.ENTITY_GAME_PIECE
        self.max_instances_in_single_tile = 1
        self.draw_order = 0
        self.__dungeon_level = None

    @property
    def dungeon_level(self):
        return self.__dungeon_level

    @dungeon_level.setter
    def dungeon_level(self, value):
        if(not self.dungeon_level is value and not value is None):
            self.fov_map = libtcod.map_new(value.width, value.height)
            self.update_calculate_dungeon_property_map(value)
        self.__dungeon_level = value

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
        for entity in self.dungeon_level.entities:
            if libtcod.map_is_in_fov(self.fov_map, entity.position.x,
                                     entity.position.y):
                seen_entities.append(entity)
        seen_entities.remove(self)
        return seen_entities

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

    def update_calculate_dungeon_property_map(self, value):
        for y in range(value.height):
            for x in range(value.width):
                terrain = value.tile_matrix[y][x].terrain
                libtcod.map_set_properties(self.fov_map, x, y,
                                           terrain.is_transparent(),
                                           terrain.is_solid())
