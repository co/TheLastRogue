import math
import random

import terrain
import rng
import graph
import direction
import dungeonlevel
import dungeonfeature
import shapegenerator
import geometry as geo
import tile


def generate_dungeon_level(depth):
    dungeon_level = generate_terrain_dungeon_level(depth)
    while not place_up_down_stairs_at_center(dungeon_level):
        dungeon_level = generate_terrain_dungeon_level(depth)
    return dungeon_level


def generate_terrain_dungeon_level(depth):
    dungeon_level = get_full_wall_dungeon(40, 40, depth)
    center_position = (dungeon_level.width / 2,
                       dungeon_level.height / 2)
    brush = SinglePointBrush(ReplaceTerrain(terrain.Floor))
    end_condition_func = CountDownCondition(dungeon_level.width *
                                            dungeon_level.height * 0.4)
    move_list = list(direction.DIRECTIONS)
    drunkard_walk(center_position, dungeon_level, brush,
                  end_condition_func, move_list)
    #cellular_automata(dungeon_level)
    return dungeon_level


def place_up_down_stairs_at_center(dungeon_level):
    center = (dungeon_level.width / 2,
              dungeon_level.height / 2)
    next_to_center = geo.add_2d(center, (0, 1))
    place_up_down_stairs(dungeon_level, center, next_to_center)
    return True


def place_up_down_stairs(dungeon_level, up_position, down_position):
    _place_feature_replace_terrain_with_floor(dungeonfeature.StairsDown(),
                                              dungeon_level, down_position)
    _place_feature_replace_terrain_with_floor(dungeonfeature.StairsUp(),
                                              dungeon_level, up_position)


def _place_feature_replace_terrain_with_floor(feature, dungeon_level,
                                              position):
    terrain.Floor().mover.replace_move(position, dungeon_level)
    feature.mover.try_move(position, dungeon_level)


def get_full_of_terrain_dungeon(terrain_class, width, height, depth):
    dungeon = get_empty_dungeon(width, height, depth)
    for y in range(height):
        for x in range(width):
            wall = terrain.Wall()
            wall.mover.try_move((x, y), dungeon)
    return dungeon


def get_full_wall_dungeon(width, height, depth):
    return get_full_of_terrain_dungeon(terrain.Wall, width,
                                       height, depth)


def get_empty_tile_matrix(width, height):
    return [[tile.Tile()
             for x in range(width)]
            for y in range(height)]


def get_empty_dungeon(width, height, depth):
    return dungeonlevel.DungeonLevel(get_empty_tile_matrix(width, height),
                                     depth)


def is_solid_ratio(dungeon_level):
    solid = 0
    for y in range(dungeon_level.height):
        for x in range(dungeon_level.width):
            tile = dungeon_level.get_tile((x, y))
            if tile.get_terrain().is_solid.value:
                solid += 1
    result = float(solid) / float(dungeon_level.width * dungeon_level.height)
    return result


def drunkard_walk(dungeon_level, start_pos, tile_brush, end_condition_func,
                  move_list=None):
    if move_list is None:
        move_list = direction.DIRECTIONS
    position = start_pos
    visited = set()
    unvisited_positions = set()
    while not end_condition_func():
        tile_brush.apply_brush(dungeon_level, position)
        visited.add(position)
        neighbors = set([geo.add_2d(position, _direction)
                         for _direction in move_list])
        unvisited_neighbors = neighbors - visited
        unvisited_positions = unvisited_positions | unvisited_neighbors
        if len(unvisited_neighbors) >= 1:
            position = random.sample(unvisited_neighbors, 1)[0]
        else:
            position = random.sample(unvisited_positions, 1)[0]
        while not dungeon_level.has_tile(position):
            position = random.sample(unvisited_positions, 1)[0]


def random_explosion(dungeon_level, start_pos, tile_brush,
                     end_condition_func, move_list=None):
    if move_list is None:
        move_list = direction.DIRECTIONS
    position = start_pos
    visited = set()
    unvisited_positions = set()
    while not end_condition_func():
        tile_brush.apply_brush(dungeon_level, position)
        visited.add(position)
        neighbors = set([geo.add_2d(position, _direction)
                         for _direction in move_list])
        unvisited_neighbors = neighbors - visited
        unvisited_positions = unvisited_positions | unvisited_neighbors
        if len(unvisited_positions) >= 1:
            position = random.sample(unvisited_positions, 1)[0]
        else:
            break


def dfs_tunnler(dungeon_level, start_position, min_length, max_length,
                tile_brush, end_condition_func, direction_list=None):
    position = start_position
    direction_ = random.sample(direction_list, 1)[0]
    while not end_condition_func():
        direction_ = direction.turn_left_or_right(direction_)
        length = random.randint(min_length, max_length)
        tile_brush.apply_brush(dungeon_level, position)
        for _ in range(length):
            position = geo.add_2d(position, direction_)
            tile_brush.apply_brush(dungeon_level, position)


def dig_out_rect(rect, dungeon_level):
    dig_out_brush = SinglePointBrush(ReplaceTerrain(terrain.Floor))
    for x in range(rect.left, rect.width):
        for y in range(rect.top, rect.height):
            dig_out_brush.apply_brush(dungeon_level, (x, y))


def cellular_automata(dungeon_level):
    for y in range(dungeon_level.height):
        for x in range(dungeon_level.width):
            position = (x, y)
            neighbors = [geo.add_2d(position, direction_)
                         for direction_ in direction.DIRECTIONS]

            solid_neighbors = 0
            for point in neighbors:
                if (not dungeon_level.has_tile(point) or
                        dungeon_level.get_tile(point).get_terrain().is_solid.value):
                    solid_neighbors += 1
            _apply_cellular_automata_rule_on_tile(dungeon_level, position,
                                                  solid_neighbors)


def _apply_cellular_automata_rule_on_tile(dungeon_level, position,
                                          number_of_solid_neighbors):
    this_terrain = dungeon_level.get_tile(position).get_terrain()
    solid_neighborhood_size = \
        number_of_solid_neighbors + (1 if this_terrain.is_solid.value else 0)
    if solid_neighborhood_size >= 5:
        terrain.Wall().mover.replace_move(position, dungeon_level)
    else:
        terrain.Floor().mover.replace_move(position, dungeon_level)


def generate_dungeon_exploded_rooms(open_area, depth):
    rooms = random.randrange(3, 12)
    room_area = open_area * 0.8 / rooms
    aprox_room_radius = math.sqrt(room_area)

    room_distance = aprox_room_radius

    grid_side = int(max(rooms / 2 + 1, math.sqrt(rooms + 1) + 1))
    triangle_points = shapegenerator.triangle_points(room_distance,
                                                     grid_side, grid_side)

    room_positions = random.sample(triangle_points, rooms)
    minor_room_positions = set()
    room_graph = graph.Graph()
    corridors_points = set()
    for room_position in room_positions:
        room_graph.add_point(room_position)
    while not room_graph.is_connected():
        edge = random.sample(room_positions, 2)
        while room_graph.has_edge(edge[0], edge[1]):
            edge = random.sample(room_positions, 2)
        room_graph.add_edge(edge[0], edge[1])
        mid_point = random.sample(shapegenerator.get_opposite_rectangle_corners(edge[0], edge[1]), 1)[0]
        minor_room_positions.add(mid_point)
        corridor = shapegenerator.three_point_rectangle_draw(edge[0], mid_point, edge[1])
        corridors_points.update(corridor)

    open_points = corridors_points
    for position in room_positions:
        room_points = \
            shapegenerator.random_explosion(position, room_area,
                                            direction.AXIS_DIRECTIONS)
        open_points.update(room_points)

    for position in minor_room_positions:
        room_points = \
            shapegenerator.random_explosion(position, room_area / 4,
                                            direction.AXIS_DIRECTIONS)
        open_points.update(room_points)

    level_shape = shapegenerator.Shape(open_points)
    frame = 2
    dungeon_rect = level_shape.calc_rect().expanded_by(frame)

    dungeon_level = get_full_wall_dungeon(dungeon_rect.width,
                                          dungeon_rect.height, depth)
    brush = SinglePointBrush(ReplaceTerrain(terrain.Floor))
    normalized_open_points = level_shape.calc_normalized_points(frame / 2)
    apply_brush_to_points(dungeon_level, normalized_open_points, brush)

    feature_positions = random.sample(normalized_open_points, 3)
    place_up_down_stairs(dungeon_level, feature_positions[0],
                         feature_positions[1])
    _place_feature_replace_terrain_with_floor(dungeonfeature.Fountain(),
                                              dungeon_level,
                                              feature_positions[2])

    return dungeon_level


def generate_dungeon_cave_floor(size, depth):
    corridor_room_area_ratio = 0.25
    corridor_area = size * corridor_room_area_ratio
    corridors_directions = direction.AXIS_DIRECTIONS
    corridors_shape = \
        shapegenerator.dfs_tunnler_with_random_restart((0, 0), 10, 16,
                                                       corridor_area,
                                                       corridors_directions)

    rooms = random.randrange(4, 8)
    room_positions = random.sample(corridors_shape, rooms)
    open_points = corridors_shape
    total_room_area = size * (1 - corridor_room_area_ratio)
    for position in room_positions:
        room_points = \
            shapegenerator.random_explosion(position, total_room_area / rooms,
                                            direction.AXIS_DIRECTIONS)
        #open_points.update(room_points)

    frame = 2
    level_shape = shapegenerator.Shape(open_points)
    dungeon_rect = level_shape.calc_rect().expanded_by(frame)

    dungeon_level = get_full_wall_dungeon(dungeon_rect.width,
                                          dungeon_rect.height, depth)

    normalized_open_points = level_shape.calc_normalized_points(frame / 2)
    brush = SinglePointBrush(ReplaceTerrain(terrain.Floor))
    apply_brush_to_points(dungeon_level, normalized_open_points, brush)

    feature_positions = random.sample(normalized_open_points, 2)
    place_up_down_stairs(dungeon_level, feature_positions[0],
                         feature_positions[1])

    drinks = 1 if rng.coin_flip() else 0
    _place_feature_replace_terrain_with_floor(dungeonfeature.Fountain(drinks),
                                              dungeon_level,
                                              feature_positions[2])
    return dungeon_level


def apply_brush_to_points(dungeon_level, points, brush):
    for point in points:
        brush.apply_brush(dungeon_level, point)


class TileBrush(object):
    def __init__(self, tile_modifier):
        self.tile_modifier = tile_modifier

    def apply_brush(self, dungeon_level, position):
        pass


class SingleShapeBrush(TileBrush):
    def __init__(self, shape, tile_modifier):
        super(SingleShapeBrush, self).__init__(tile_modifier)
        self.shape = shape

    def apply_brush(self, dungeon_level, position):
        for point in self.shape:
            dungeon_position = geo.add_2d(point, position)
            self.tile_modifier.modify(dungeon_level, dungeon_position)


class RandomShapeBrush(TileBrush):
    def __init__(self, shapes, tile_modifier):
        super(RandomShapeBrush, self).__init__(tile_modifier)
        self.shapes = shapes
        self.tile_modifier = tile_modifier

    def apply_brush(self, dungeon_level, position):
        shape = random.sample(self.shapes, 1)[0]
        for point in shape:
            dungeon_position = geo.add_2d(point, position)
            self.tile_modifier.modify(dungeon_level, dungeon_position)


class RandomTriShapedBrush(RandomShapeBrush):
    def __init__(self, tile_modifier):
        shapes = [[direction.CENTER, direction.UP, direction.LEFT],
                  [direction.CENTER, direction.UP, direction.RIGHT],
                  [direction.CENTER, direction.DOWN, direction.LEFT],
                  [direction.CENTER, direction.DOWN, direction.RIGHT]]
        super(RandomTriShapedBrush, self).__init__(shapes, tile_modifier)


class RandomTriLineShapedBrush(RandomShapeBrush):
    def __init__(self, tile_modifier):
        shapes = [[direction.CENTER, direction.UP, direction.DOWN],
                  [direction.CENTER, direction.LEFT, direction.RIGHT]]
        super(RandomTriLineShapedBrush, self).__init__(shapes, tile_modifier)


class SinglePointBrush(SingleShapeBrush):
    def __init__(self, tile_modifier):
        super(SinglePointBrush, self).__init__([(0, 0)],
                                               tile_modifier)


class SquareBrush(SingleShapeBrush):
    def __init__(self, tile_modifier):
        super(SquareBrush, self).__init__([(0, 0), (1, 0), (0, 1), (1, 1)],
                                          tile_modifier)


class TileModifier(object):
    def __init__(self):
        pass

    def modify(self, position, dungeon_level):
        pass


class ReplaceTerrain(TileModifier):
    def __init__(self, terrain_class):
        super(ReplaceTerrain, self).__init__()
        self.terrain_class = terrain_class

    def modify(self, dungeon_level, position):
        terrain_to_modify = self.terrain_class()
        terrain_to_modify.mover.replace_move(position, dungeon_level)


class CountDownCondition():
    def __init__(self, calls_left):
        self._calls_left = calls_left

    def __call__(self):
        self._calls_left -= 1
        return self._calls_left <= 0
