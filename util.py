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
           time_stamp <= self._time_stamps[entity.description.name]):
            return True
        return False

    def _get_destinations(self, entity, position):
        class_cache = self._cache[entity.description.name]
        return class_cache[position]

    def _has_destinations(self, entity, position):
        if not entity.description.name in self._cache.keys():
            return False
        class_cache = self._cache[entity.description.name]
        if not position in class_cache.keys():
            return False
        return True

    def _set_destinations(self, entity, click_of_points):
        if not entity.description.name in self._cache.keys():
            self._cache[entity.description.name] = {}
        class_cache = self._cache[entity.description.name]
        for point in click_of_points:
            class_cache[point] = click_of_points
        # Maybe a per point time_stamp is necessary?
        self._time_stamps[entity.description.name] = turn.current_turn

    def get_walkable_positions(self, entity, position, dungeon_level):
        time_stamp = dungeon_level.terrain_changed_timestamp
        if not self._has_destinations_newer_than(entity, position, time_stamp):
            self._calculate_walkable_positions_from_entity_position(entity, position, dungeon_level)
        return self._get_destinations(entity, position)

    def _calculate_walkable_positions_from_entity_position(self, entity, position, dungeon_level):
        visited = set()
        visited.add(position)
        queue = [position]
        queue.extend(_get_walkable_neighbors(entity, position, dungeon_level))
        while len(queue) > 0:
            position = queue.pop(0)
            while len(queue) > 0 and position in visited:
                position = queue.pop(0)
            visited.add(position)
            neighbors = set(_get_walkable_neighbors(entity, position, dungeon_level)) - visited
            queue.extend(neighbors)
        visited = list(visited)
        self._set_destinations(entity, visited)


def _position_has_item_with_auto_pick_up(position, dungeon_level):
    tile = dungeon_level.get_tile(position)
    item = tile.get_first_item()
    if item and item.has("player_auto_pick_up"):
        return True
    return False


def get_closest_unseen_walkable_position(entity, position, dungeon_level):
    visited = set()
    visited.add(position)
    queue = [position]
    queue.extend(_get_walkable_neighbors(entity, position, dungeon_level))
    while len(queue) > 0:
        position = queue.pop(0)
        while len(queue) > 0 and position in visited:
            position = queue.pop(0)
        if not entity.memory_map.has_seen_position(position):
            return position_or_walkable_neighbor(position, entity, dungeon_level)
        elif _position_has_item_with_auto_pick_up(position, dungeon_level):
            return position
        visited.add(position)
        neighbors = set(_get_walkable_neighbors_or_unseen(position, entity, dungeon_level)) - visited
        queue.extend(neighbors)
    return None


def position_or_walkable_neighbor(position, entity, dungeon_level):
    tile = dungeon_level.get_tile(position)
    if entity.mover.can_pass_terrain(tile.get_terrain()):
        return position
    else:
        return _get_walkable_neighbors(entity, position, dungeon_level)[0]


def _get_walkable_neighbors(entity, position, dungeon_level):
    result_positions = []
    for direction_ in direction.DIRECTIONS:
        neighbor_position = geo.add_2d(position, direction_)
        try:
            neighbor = dungeon_level.get_tile(neighbor_position)
            if entity.mover.can_pass_terrain(neighbor.get_terrain()):
                result_positions.append(neighbor_position)
        except IndexError:
            pass
    return result_positions


def _get_walkable_neighbors_or_unseen(position, entity, dungeon_level):
    result_positions = []
    for direction_ in direction.DIRECTIONS:
        neighbor_position = geo.add_2d(position, direction_)
        try:
            neighbor = dungeon_level.get_tile(neighbor_position)
            if (entity.mover.can_pass_terrain(neighbor.get_terrain()) or
                    not entity.memory_map.has_seen_position(neighbor_position)):
                result_positions.append(neighbor_position)
        except IndexError:
            pass
    return result_positions


def entity_skip_turn(source_entity, target_entity):
    add_spoof_effect = AddSpoofChild(source_entity, DoNothingActor(), gametime.single_turn)
    target_entity.effect_queue.add(add_spoof_effect)


def entity_skip_step(source_entity, target_entity):
    add_spoof_effect = AddSpoofChild(source_entity, ImmobileStepper(), gametime.single_turn)
    target_entity.effect_queue.add(add_spoof_effect)
