from actor import DoNothingActor
from entityeffect import AddSpoofChild
import gametime
from mover import ImmobileStepper
import turn
import direction
import geometry as geo


class WalkableDestinatinationsPath(object):
    def __init__(self):
        self._cache = {}
        self._time_stamps = {}

    def _has_destinations_newer_than(self, entity, position, time_stamp):
        if(self._has_destinations(entity, position) and
           time_stamp <= self._time_stamps[entity.__class__]):
            return True
        return False

    def _get_destinations(self, entity, position):
        class_cache = self._cache[entity.__class__]
        return class_cache[position]

    def _has_destinations(self, entity, position):
        if not entity.__class__ in self._cache.keys():
            return False
        class_cache = self._cache[entity.__class__]
        if not position in class_cache.keys():
            return False
        return True

    def _set_destinations(self, entity, click_of_points):
        if not entity.__class__ in self._cache.keys():
            self._cache[entity.__class__] = {}
        class_cache = self._cache[entity.__class__]
        for point in click_of_points:
            class_cache[point] = click_of_points
        # Maybe a per point time_stamp is necessary?
        self._time_stamps[entity.__class__] = turn.current_turn

    def get_walkable_positions(self, entity, position):
        time_stamp = entity.dungeon_level.value.terrain_changed_timestamp
        if(not self._has_destinations_newer_than(entity, position,
                                                 time_stamp)):
            self._calculate_walkable_positions_from_entity_position(entity,
                                                                    position)
        return self._get_destinations(entity, position)

    def _calculate_walkable_positions_from_entity_position(self, entity, position):
        visited = set()
        visited.add(position)
        queue = [position]
        queue.extend(_get_walkable_neighbors(position, entity))
        while len(queue) > 0:
            position = queue.pop(0)
            while len(queue) > 0 and position in visited:
                position = queue.pop(0)
            visited.add(position)
            neighbors = set(_get_walkable_neighbors(position, entity)) - visited
            queue.extend(neighbors)
        visited = list(visited)
        self._set_destinations(entity, visited)


def _position_has_item_with_auto_pick_up(position, entity):
    tile = entity.dungeon_level.value.get_tile(position)
    item = tile.get_first_item()
    if item and item.has("player_auto_pick_up"):
        return True
    return False


def get_closest_unseen_walkable_position(entity, position):
    visited = set()
    visited.add(position)
    queue = [position]
    queue.extend(_get_walkable_neighbors(position, entity))
    while len(queue) > 0:
        position = queue.pop(0)
        while len(queue) > 0 and position in visited:
            position = queue.pop(0)
        if not entity.memory_map.has_seen_position(position):
            return position_or_walkable_neighbor(position, entity)
        elif _position_has_item_with_auto_pick_up(position, entity):
            return position
        visited.add(position)
        neighbors = set(_get_walkable_neighbors_or_unseen(position, entity)) - visited
        queue.extend(neighbors)
    return None


def position_or_walkable_neighbor(position, entity):
    tile = entity.dungeon_level.value.get_tile(position)
    if entity.mover.can_pass_terrain(tile.get_terrain()):
        return position
    else:
        return _get_walkable_neighbors(position, entity)[0]


def _get_walkable_neighbors(position, entity):
    result_positions = []
    for direction_ in direction.DIRECTIONS:
        neighbor_position = geo.add_2d(position, direction_)
        try:
            neighbor = entity.dungeon_level.value.get_tile(neighbor_position)
            if entity.mover.can_pass_terrain(neighbor.get_terrain()):
                result_positions.append(neighbor_position)
        except IndexError:
            pass
    return result_positions


def _get_walkable_neighbors_or_unseen(position, entity):
    result_positions = []
    for direction_ in direction.DIRECTIONS:
        neighbor_position = geo.add_2d(position, direction_)
        try:
            neighbor = entity.dungeon_level.value.get_tile(neighbor_position)
            if (entity.mover.can_pass_terrain(neighbor.get_terrain()) or
                    not entity.memory_map.has_seen_position(neighbor_position)):
                result_positions.append(neighbor_position)
        except IndexError:
            pass
    return result_positions


def entity_skip_turn(source_entity, target_entity):
    add_spoof_effect = AddSpoofChild(source_entity, DoNothingActor(), gametime.single_turn)
    target_entity.effect_queue.add(add_spoof_effect)
