import turn
import constants
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
        if(not entity.__class__ in self._cache.keys()):
            return False
        class_cache = self._cache[entity.__class__]
        if(not position in class_cache.keys()):
            return False
        return True

    def _set_destinations(self, entity, click_of_points):
        if(not entity.__class__ in self._cache.keys()):
            self._cache[entity.__class__] = {}
        class_cache = self._cache[entity.__class__]
        for point in click_of_points:
            class_cache[point] = click_of_points
        # Maybe a per point time_stamp is necessary?
        self._time_stamps[entity.__class__] = turn.current_turn

    def get_walkable_positions_from_my_position(self, entity, position):
        time_stamp = entity.dungeon_level.terrain_changed_timestamp
        if(not self._has_destinations_newer_than(entity, position,
                                                 time_stamp)):
            self._calculate_walkable_positions_from_entity_position(entity,
                                                                    position)
        return self._get_destinations(entity, position)

    def _calculate_walkable_positions_from_entity_position(self, entity,
                                                           position):
        visited = set()
        visited.add(position)
        queue = [position]
        queue.extend(self._get_walkable_neighbors(position, entity))
        while (len(queue) > 0):
            position = queue.pop()
            while(len(queue) > 0 and position in visited):
                position = queue.pop()
            visited.add(position)
            neighbors = set(self._get_walkable_neighbors(position, entity))\
                - visited
            queue.extend(neighbors)
        visited = list(visited)
        self._set_destinations(entity, visited)

    def _get_walkable_neighbors(self, position, entity):
        result_positions = []
        for direction in constants.DIRECTIONS_LIST:
            neighbor_position = geo.add_2d(position, direction)
            try:
                neighbor = entity.dungeon_level.get_tile(neighbor_position)
                if(entity._can_pass_terrain(neighbor.get_terrain())):
                    result_positions.append(neighbor_position)
            except IndexError:
                pass
        return result_positions
