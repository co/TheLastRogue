import terrain
import dungeonlevel
import dungeonfeature
import vector2d as v2d
import random
import constants
import tile


def generate_dungeon_level(depth):
    dungeon_level = generate_terrain_dungeon_level(depth)
    while(not place_up_down_stairs(dungeon_level)):
        dungeon_level = generate_terrain_dungeon_level(depth)
    return dungeon_level


def generate_terrain_dungeon_level(depth):
    dungeon_level = get_full_wall_dungeon(40, 40, depth)
    center_position = v2d.Vector2D(dungeon_level.width / 2,
                                   dungeon_level.height / 2)
    brush = SinglePointBrush(ReplaceTerrain(terrain.Floor))
    end_condition = CountDownCondition(dungeon_level.width *
                                       dungeon_level.height * 0.4)
    move_list = list(constants.DIRECTIONS.values())
    drunkard_walk(center_position, dungeon_level, brush,
                  end_condition, move_list)
    #cellular_automata(dungeon_level)
    return dungeon_level


def place_up_down_stairs(dungeon_level):
    center = v2d.Vector2D(dungeon_level.width / 2,
                          dungeon_level.height / 2)
    next_to_center = center + v2d.Vector2D(0, 1)
    _place_feature_replace_terrain_with_floor(dungeonfeature.StairsDown(),
                                              center, dungeon_level)
    _place_feature_replace_terrain_with_floor(dungeonfeature.StairsUp(),
                                              next_to_center, dungeon_level)
    return True


def _place_feature_replace_terrain_with_floor(feature, position,
                                              dungeon_level):
    feature.try_move(position, dungeon_level)
    terrain.Floor().replace_move(position, dungeon_level)


def get_full_of_terrain_dungeon(terrain_class, width, height, depth):
    dungeon = get_empty_dungeon(width, height, depth)
    for y in range(height):
        for x in range(width):
            wall = terrain.Wall()
            wall.try_move(v2d.Vector2D(x, y), dungeon)
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
            tile = dungeon_level.get_tile(v2d.Vector2D(x, y))
            if tile.get_terrain().is_solid():
                solid += 1
    result = float(solid) / float(dungeon_level.width * dungeon_level.height)
    return result


def drunkard_walk(start_pos, dungeon_level, tile_brush, end_condition,
                  move_list=None):
    if move_list is None:
        move_list = constants.DIRECTIONS_LIST
    position = start_pos.copy()
    visited = set()
    unvisited_positions = set()
    while not end_condition():
        tile_brush.apply_brush(position, dungeon_level)
        visited.add(position)
        neighbors = set([position + direction
                         for direction in move_list])
        unvisited_neighbors = neighbors - visited
        unvisited_positions = unvisited_positions | unvisited_neighbors
        if(len(unvisited_neighbors) >= 1):
            position = random.sample(unvisited_neighbors, 1)[0]
        else:
            position = random.sample(unvisited_positions, 1)[0]
        while(not dungeon_level.has_tile(position)):
            position = random.sample(unvisited_positions, 1)[0]


def random_exlosion(start_pos, dungeon_level, tile_brush,
                    end_condition, move_list=None):
    if move_list is None:
        move_list = constants.DIRECTIONS_LIST
    position = start_pos.copy()
    visited = set()
    unvisited_positions = set()
    while not end_condition():
        tile_brush.apply_brush(position, dungeon_level)
        visited.add(position)
        neighbors = set([position + direction
                         for direction in move_list])
        unvisited_neighbors = neighbors - visited
        unvisited_positions = unvisited_positions | unvisited_neighbors
        if(len(unvisited_positions) >= 1):
            position = random.sample(unvisited_positions, 1)[0]
        else:
            break


def cellular_automata(dungeon_level):
    for y in range(dungeon_level.height):
        for x in range(dungeon_level.width):
            position = v2d.Vector2D(x, y)
            neighbors = [position + direction
                         for direction in constants.DIRECTIONS_LIST]

            solid_neighbors = 0
            for point in neighbors:
                if(not dungeon_level.has_tile(point) or
                   dungeon_level.get_tile(point).get_terrain().is_solid()):
                    solid_neighbors += 1
            _apply_cellular_automata_rule_on_tile(position, dungeon_level,
                                                  solid_neighbors)


def _apply_cellular_automata_rule_on_tile(position, dungeon_level,
                                          number_of_solid_neighbors):
    this_terrain = dungeon_level.get_tile(position).get_terrain()
    solid_neighborhood_size =\
        number_of_solid_neighbors + (1 if this_terrain.is_solid() else 0)
    if solid_neighborhood_size >= 5:
        terrain.Wall().replace_move(position, dungeon_level)
    else:
        terrain.Floor().replace_move(position, dungeon_level)


class TileBrush(object):
    def __init__(self, tile_modifier):
        self.tile_modifier = tile_modifier

    def apply_brush(self, position, dungeon_level):
        pass


class SingleShapeBrush(TileBrush):
    def __init__(self, shape, tile_modifier):
        super(SingleShapeBrush, self).__init__(tile_modifier)
        self.shape = shape

    def apply_brush(self, position, dungeon_level):
        for point in self.shape:
            dungeon_position = point + position
            self.tile_modifier.modify(dungeon_position, dungeon_level)


class RandomShapeBrush(TileBrush):
    def __init__(self, shapes, tile_modifier):
        super(RandomShapeBrush, self).__init__(tile_modifier)
        self.shapes = shapes
        self.tile_modifier = tile_modifier

    def apply_brush(self, position, dungeon_level):
        shape = random.sample(self.shapes, 1)[0]
        for point in shape:
            dungeon_position = point + position
            self.tile_modifier.modify(dungeon_position, dungeon_level)


class RandomTriShapedBrush(RandomShapeBrush):
    def __init__(self, tile_modifier):
        face = constants.DIRECTIONS
        center = v2d.Vector2D(0, 0)
        shapes = [[center, face["N"], face["W"]],
                  [center, face["N"], face["E"]],
                  [center, face["S"], face["W"]],
                  [center, face["S"], face["E"]]]
        super(RandomTriShapedBrush, self).__init__(shapes, tile_modifier)


class SinglePointBrush(SingleShapeBrush):
    def __init__(self, tile_modifier):
        super(SinglePointBrush, self).__init__([v2d.Vector2D(0, 0)],
                                               tile_modifier)


class SquareBrush(SingleShapeBrush):
    def __init__(self, tile_modifier):
        super(SquareBrush, self).__init__([v2d.Vector2D(0, 0),
                                           v2d.Vector2D(1, 0),
                                           v2d.Vector2D(0, 1),
                                           v2d.Vector2D(1, 1)],
                                          tile_modifier)


class TileModifier(object):
    def __init__(self):
        pass

    def modify(self, tile):
        pass


class ReplaceTerrain(TileModifier):
    def __init__(self, terrain_class):
        self.terrain_class = terrain_class

    def modify(self, position, dungeon_level):
        terrain_to_modify = self.terrain_class()
        terrain_to_modify.replace_move(position, dungeon_level)


class CountDownCondition():
    def __init__(self, calls_left):
        self._calls_left = calls_left

    def __call__(self):
        self._calls_left -= 1
        return self._calls_left <= 0
