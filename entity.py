import random
import rng
import turn
import gametime
import damage
import numpy
import geometry as geo
import counter
import constants
import gamepiece
import entityeffect
import equipment
import terrain
import libtcodpy as libtcod


class Faction(object):
    PLAYER = 0
    MONSTER = 1


class StatusFlags(object):
    INVISIBILE = 0
    SEE_INVISIBILITY = 1
    FLYING = 2
    HAS_MIND = 3
    CAN_OPEN_DOORS = 4
    SWALLOWED_BY_SLIME = 5


class Entity(gamepiece.GamePiece):

    def __init__(self, game_state):
        super(Entity, self).__init__()
        self.hp = counter.Counter(1, 1)
        self._sight_radius = 6
        self._strength = 1
        self.equipment = equipment.Equipment(self)

        self._faction = Faction.MONSTER
        self.effect_queue = entityeffect.EffectQueue()
        self._temporary_status_flags = set()
        self._permanent_status_flags = set()
        self._permanent_status_flags.add(StatusFlags.CAN_OPEN_DOORS)

        self.game_state = game_state
        self.piece_type = gamepiece.GamePieceType.ENTITY
        self.max_instances_in_single_tile = 1

        self.path = None
        self.__dungeon_level = None
        self._init_entity_effects()

        self.newly_spent_energy = 0
        self.energy = 0
        self.energy_recovery = gametime.normal_energy_gain
        self.movement_speed = gametime.single_turn
        self.attack_speed = gametime.single_turn

        self.last_dungeon_map_update_timestamp = -1

    def _init_entity_effects(self):
        can_open_doors_flag = StatusFlags.CAN_OPEN_DOORS
        effect = entityeffect.StatusAdder(self, self,
                                          can_open_doors_flag,
                                          time_to_live=numpy.inf)
        self.add_entity_effect(effect)

    @property
    def dungeon_level(self):
        return self.__dungeon_level

    @dungeon_level.setter
    def dungeon_level(self, value):
        if((not self.dungeon_level is value) and (not value is None)):
            self.__dungeon_level = value
            self.dungeon_map = libtcod.map_new(value.width, value.height)
            self.update_dungeon_map()
            self.path = libtcod.path_new_using_map(self.dungeon_map, 1.0)
            self._signal_new_dungeon_level()

    @property
    def state_stack(self):
        return self.game_state.current_stack

    def _signal_new_dungeon_level(self):
        pass

    def act(self):
        pass

    def step_random_direction(self):
        direction = random.sample(list(constants.DIRECTIONS.values()), 1)
        new_position = geo.add_2d(self.position, direction[0])
        self.try_step_to(new_position)

    def try_step_to(self, position):
        if(self.has_status(StatusFlags.SWALLOWED_BY_SLIME)):
            escape_successful = self.try_to_escape_slime(position)
            if(not escape_successful):
                return True
        terrain_to_step = self.dungeon_level.get_tile(position).get_terrain()
        if(self.try_open_door(terrain_to_step)):
            return True
        if(self.try_hit(position)):
            return True
        if(self.try_move(position)):
            return True
        return False

    def try_open_door(self, terrain_to_step):
        """
        Will try to open the door, if the door is already open return False.
        """
        if(isinstance(terrain_to_step, terrain.Door)):
            door = terrain_to_step
            if(not door.is_open):
                door.open()
                return True
        return False

    def get_entity_sharing_my_position(self):
        """
        Sometimes two entities can share a tile this method
        returns the other entity if this is case.
        If the number of entities of this tile is neither 1 or 2
        raise an exception as this is an invalid state.
        """
        entities_on_my_tile =\
            self.dungeon_level.get_tile(self.position).get_entities()
        if(len(entities_on_my_tile) == 1):
            return None
        if(len(entities_on_my_tile) != 2):
            raise
        return next(entity for entity in entities_on_my_tile
                    if not entity is self)

    def try_to_escape_slime(self, position):
        """
        Assumes the entity is trapped by a slime,
        if escape is successful return true otherwise false.
        """
        slime = self.get_entity_sharing_my_position()
        if not slime is None:
            self.hit(slime)
        escape_successful = rng.coin_flip() and rng.coin_flip()
        return escape_successful

    def try_move(self, new_position, new_dungeon_level=None):
        """
        Will attempt to move the entity to a new dungeon_level/position.
        If the move is successful return true otherwise false.
        """
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
            self.update_fov()
        return move_succeded

    def try_remove_from_dungeon(self):
        """
        Will attempt to remove the entity from the dungeon_level/position.
        If the remove is successful return true otherwise false.
        """
        old_dungeon_level = self.dungeon_level
        remove_succeded = super(Entity, self).\
            try_remove_from_dungeon()
        if(remove_succeded and (not old_dungeon_level is None)):
            old_dungeon_level.remove_entity_if_present(self)
        return remove_succeded

    def get_seen_entities(self):
        seen_entities = []
        for entity in self.dungeon_level.entities:
            if self.can_see_point(entity.position):
                seen_entities.append(entity)
        return [entity for entity in seen_entities if not entity is self]

    def get_seen_entities_closest_first(self):
        return sorted(self.get_seen_entities(),
                      key=lambda entity: geo.chess_distance(self.position,
                                                            entity.position))

    def get_closest_seen_entity(self):
        closest_seen_entities = self.get_seen_entities_closest_first()
        if(len(closest_seen_entities) < 1):
            return None
        return closest_seen_entities[0]

    def can_see_point(self, point):
        x, y = point
        return libtcod.map_is_in_fov(self.dungeon_map, x, y)

    def hurt(self, damage, entity=None):
        self.hp.decrease(damage)
        if(self.is_dead):
            self.killer = entity

    def heal(self, health):
        self.hp.increase(health)

    def is_dead(self):
        return self.hp.value == 0

    def try_hit(self, position):
        entity = self.dungeon_level.get_tile(position).get_first_entity()
        if(entity is None or
           entity._faction == self._faction):
            return False
        self.hit(entity)
        return True

    def _unarmed_damage(self):
        damage_types = [damage.DamageTypes.BLUNT, damage.DamageTypes.PHYSICAL]
        return damage.Damage(self._strength, self._strength / 2, damage_types)

    def rock_throwing_damage(self):
        return self._unarmed_damage()

    def hit(self, target_entity):
        # implement melee weapon damage here.
        self._unarmed_damage().damage_entity(self, target_entity)

    def add_entity_effect(self, effect):
        self.effect_queue.add(effect)

    def update_effect_queue(self):
        self.effect_queue.update()

    def update_fov(self):
        x, y = self.position
        libtcod.map_compute_fov(self.dungeon_map, x, y,
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

    def print_is_transparent_map(self):
        for y in range(libtcod.map_get_height(self.dungeon_map)):
            line = ""
            for x in range(libtcod.map_get_width(self.dungeon_map)):
                if(libtcod.map_is_transparent(self.dungeon_map, x, y)):
                    line += " "
                else:
                    line += "#"
            print(line)

    def print_visible_map(self):
        for y in range(libtcod.map_get_height(self.dungeon_map)):
            line = ""
            for x in range(libtcod.map_get_width(self.dungeon_map)):
                if(libtcod.map_is_in_fov(self.dungeon_map, x, y)):
                    line += " "
                else:
                    line += "#"
            print(line)

    def try_step_path(self):
        if(not self.has_path()):
            return False
        x, y = libtcod.path_walk(self.path, True)
        step_succeeded = self.try_step_to((x, y))
        return step_succeeded

    def set_path_to_random_walkable_point(self):
        positions = self.get_walkable_positions_from_my_position()
        destination = random.sample(positions, 1)[0]
        sx, sy = self.position
        dx, dy = destination
        libtcod.path_compute(self.path, sx, sy, dx, dy)

    def has_status(self, status):
        return status in (self._temporary_status_flags |
                          self._permanent_status_flags)

    def add_status(self, status):
        return self._temporary_status_flags.add(status)

    def add_temporary_status(self, status):
        return self._temporary_status_flags.add(status)

    def add_permanent_status(self, status):
        return self._permanent_status_flags.add(status)

    def clear_all_temporary_status_flags(self):
        self._temporary_status_flags = set()

    def _can_pass_terrain(self, terrain_to_pass):
        if(terrain_to_pass is None):
            return False
        if(not terrain_to_pass.is_solid()):
            return True
        if(self.has_status(StatusFlags.CAN_OPEN_DOORS) and
           isinstance(terrain_to_pass, terrain.Door)):
            return True
        return False

    def get_walkable_positions_from_my_position(self):
        return self.dungeon_level.walkable_destinations.\
            get_walkable_positions_from_my_position(self, self.position)

    def update_dungeon_map_if_its_old(self):
        if(self.dungeon_level.terrain_changed_timestamp >
           self.last_dungeon_map_update_timestamp):
            self.update_dungeon_map()

    def update_dungeon_map(self):
        for y in range(self.dungeon_level.height):
            for x in range(self.dungeon_level.width):
                terrain = self.dungeon_level.tile_matrix[y][x].get_terrain()
                libtcod.map_set_properties(self.dungeon_map, x, y,
                                           terrain.is_transparent(),
                                           self._can_pass_terrain(terrain))
        self.last_dungeon_map_update_timestamp = turn.current_turn
        self.update_fov()

    def piece_copy(self, copy=None):
        if(copy is None):
            copy = self.__class__(self.game_state)
        copy._position = self._position
        copy.dungeon_level = self.dungeon_level
        copy.piece_type = self.piece_type
        copy.max_instances_in_single_tile = self.max_instances_in_single_tile
        copy.draw_order = self.draw_order
        return copy
