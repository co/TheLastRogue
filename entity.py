import random
import colors
import actor
import rng
import turn
import gametime
import damage
import geometry as geo
import counter
import direction
import gamepiece
import entityeffect
import equipment
import terrain
import libtcodpy as libtcod


class Entity(actor.Actor):
    """
    Abstract class representing an being/entity in the game.

    Attributes:
        piece_type (GamePieceType): Denotes that Item and all its
                                    subclasses are of type ENTITY.
        max_instances_in_single_tile: The number of allowed pieces of this
                                      types on a tile.
        hp (Counter): The current and max health the entity has.
        strength: The strength of the entity.
        sight_radius: The half the side of the square the entity can see.
        movement_speed: The time it takes for the entity to take a step.
        attack_speed: The time it takes for the make one combat swing.
        equipment: Represents the equipment the entity is wearing.
        game_state: The current GameState, usually used to spawn menus.
        path: The path to a destination the entity is heading towards.
        last_dungeon_map_update_timestamp: The time stamp for the last time
                                        map of the current dungeon_map
                                        was calculated.
    """
    def __init__(self, game_state):
        super(Entity, self).__init__()
        self.hp = counter.Counter(1, 1)
        self.strength = 1

        self.movement_speed = gametime.single_turn
        self.attack_speed = gametime.single_turn

        self.sight_radius = 6
        self.equipment = equipment.Equipment(self)

        self._faction = Faction.MONSTER
        self._effect_queue = entityeffect.EffectQueue()
        self._temporary_status_flags = set()
        self._permanent_status_flags = set()
        self._permanent_status_flags.add(StatusFlags.CAN_OPEN_DOORS)
        self._permanent_status_flags.add(StatusFlags.LEAVES_CORPSE)

        self.game_state = game_state
        self.piece_type = gamepiece.GamePieceType.ENTITY
        self.max_instances_in_single_tile = 1

        self.path = None
        self._dungeon_level = None

        self.last_dungeon_map_update_timestamp = -1

    @property
    def dungeon_level(self):
        """
        Gets the dungeon_level the entity is currently in.
        """
        return self._dungeon_level

    @dungeon_level.setter
    def dungeon_level(self, value):
        """
        Sets current dungeon_level of the entity.
        Also updates the visibility/solidity of the dungeon_level tiles.
        """
        if((not self.dungeon_level is value) and (not value is None)):
            self._dungeon_level = value
            self.dungeon_map = libtcod.map_new(value.width, value.height)
            self.update_dungeon_map()
            self.path = libtcod.path_new_using_map(self.dungeon_map, 1.0)
            self._signal_new_dungeon_level()

    @property
    def state_stack(self):
        """
        The StateStack of the current game.
        """
        return self.game_state.current_stack

    def _signal_new_dungeon_level(self):
        """
        Hook function that will be called each
        the entity is moved to a new DungeonLevel.
        """
        pass

    """
    Tries to make the entity step to a random direction.
    If the step succeeds True is return otherwise False.
    """
    def try_step_random_direction(self):
        random_direction = random.sample(list(direction.DIRECTIONS), 1)[0]
        new_position = geo.add_2d(self.position, random_direction)
        return self.try_move_to(new_position)

    def try_move_to(self, position):
        """
        Tries to move the entity to a position.

        If there is a unfriendly entity in the way hit it instead.
        If there is a door in the way try to open it.
        If an action is taken return True otherwise return False.

        Args:
            position (int, int): The position the entity tries to move to.
        """

        if(self.has_status(StatusFlags.SWALLOWED_BY_SLIME)):
            escape_successful = self.try_to_escape_slime(position)
            if(not escape_successful):
                return True
        terrain_to_step = self.dungeon_level.get_tile(position).get_terrain()
        if(isinstance(terrain_to_step, terrain.Door) and
           self.try_open_door(terrain_to_step)):
            return True
        if(self.try_hit(position)):
            return True
        if(self.try_move(position)):
            return True
        return False

    def try_open_door(self, door):
        """
        Will try to open the door.
        If the entity can't open doors or
        the door is already open return False.

        Args:
            door (Door): The door terrain that should be opened)
        """
        if(self.has_status(StatusFlags.CAN_OPEN_DOORS) and not door.is_open):
            door.open()
            return True
        return False

    def get_entity_sharing_my_position(self):
        """
        Sometimes two entities can share a tile this method
        returns the other entity if this is currently the case.
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

    def try_to_escape_slime(self):
        """
        Assumes the entity is trapped by a slime,
        if escape is successful return true otherwise false.
        """
        slime = self.get_entity_sharing_my_position()
        if not slime is None:
            self.hit(slime)
        escape_successful = rng.coin_flip() and rng.coin_flip()
        return escape_successful

    def get_seen_entities(self):
        """
        Gets all entities seen by this entity not including self.
        """
        seen_entities = []
        for entity in self.dungeon_level.entities:
            if self.can_see_point(entity.position):
                seen_entities.append(entity)
        return [entity for entity in seen_entities if not entity is self]

    def get_seen_entities_closest_first(self):
        """
        Gets all seen entities sorted on distance from self not including self.
        """
        return sorted(self.get_seen_entities(),
                      key=lambda entity: geo.chess_distance(self.position,
                                                            entity.position))

    def get_closest_seen_entity(self):
        """
        Gets the closest of all seen entities not including self.
        """
        closest_seen_entities = self.get_seen_entities_closest_first()
        if(len(closest_seen_entities) < 1):
            return None
        return closest_seen_entities[0]

    def can_see_point(self, point):
        """
        Checks if a particular point is visible to this entity.

        Args:
            point (int, int): The point to check.
        """
        x, y = point
        return libtcod.map_is_in_fov(self.dungeon_map, x, y)

    def hurt(self, damage, entity=None):
        """
        Damages the entity by reducing hp by damage.

        Args:
            damage: The ammount of damage caused.
            entity: The entity that caused the damage (if any)
        """
        self.hp.decrease(damage)
        self.gfx_char.set_fg_blink_colors([colors.LIGHT_PINK, colors.RED])
        if(self.is_dead):
            self.killer = entity

    def heal(self, health):
        """
        Heals increases the current hp by health.

        Args:
            heal: The amount of health that was regained.
        """
        self.hp.increase(health)

    def is_dead(self):
        """
        Returns True if the entity is considered dead.
        """
        return self.hp.value == 0

    def try_hit(self, position):
        """
        Tries to hit an entity at a position.

        Returns False if there is no entity
        there or the entity is of the same faction.

        Args:
            position(int, int): The position that the entity tries to hit.
        """
        entity = self.dungeon_level.get_tile(position).get_first_entity()
        if(entity is None or
           entity._faction == self._faction):
            return False
        self.hit(entity)
        return True

    def _unarmed_damage(self):
        """
        Calculates an instance of damage
        caused by an unarmed hit by the entity.
        """
        damage_types = [damage.DamageTypes.BLUNT, damage.DamageTypes.PHYSICAL]
        return damage.Damage(self.strength, self.strength / 2, damage_types)

    def rock_throwing_damage(self):
        """
        Calculates an instance of damage
        caused by a rock throw by the entity.
        """
        return self._unarmed_damage()

    def hit(self, target_entity):
        """
        Causes the entity to hit the target entity.

        Args:
            target_entity: The entity that this entity is trying to hit.
        """
        # implement melee weapon damage here.
        self._unarmed_damage().damage_entity(self, target_entity)

    def add_entity_effect(self, effect):
        """
        Adds an entity effect to the effect queue of this entity.

        Args:
            effect (EntityEffect): The effect that is to be added to the queue.
        """
        self._effect_queue.add(effect)

    def remove_entity_effect(self, effect):
        """
        Removes an entity effect from the effect queue of this entity.

        Args:
            effect (EntityEffect): The effect that will be removed.
        """
        self._effect_queue.remove(effect)

    def update_effect_queue(self, time_spent):
        """
        Applies all the effects in the effect queue to this entity.

        Args:
            time_spent: The game time between each call of this method.
        """
        self._effect_queue.update(time_spent)

    def update_fov(self):
        x, y = self.position
        libtcod.map_compute_fov(self.dungeon_map, x, y,
                                self.sight_radius, True)

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
        step_succeeded = self.try_move_to((x, y))
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

    def on_death(self):
        return

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
        return copy

    def _update_once_a_tick(self, time_spent):
        self.equipment.execute_equip_effects()
        self.clear_all_temporary_status_flags()
        self.update_effect_queue(time_spent)
        self.update_dungeon_map_if_its_old()
