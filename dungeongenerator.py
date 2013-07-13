import terrain
import dungeonlevel
import vector2d
import random
import constants
import tile


def get_full_of_terrain_dungeon(terrain_class, width, height, depth):
    dungeon = get_empty_dungeon(width, height, depth)
    for y in range(height):
        for x in range(width):
            wall = terrain.Wall()
            wall.try_move(vector2d.Vector2D(x, y), dungeon)
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
            tile = dungeon_level.get_tile(vector2d.Vector2D(x, y))
            if tile.get_terrain().is_solid():
                solid += 1
    result = float(solid) / float(dungeon_level.width * dungeon_level.height)
    return result


def drunkard_walk(start_pos, dungeon_level, tile_brush, end_condition):
    position = start_pos.copy()
    visited = set()
    unvisited_positions = set()
    while not end_condition():
        tile_brush.apply_brush(position, dungeon_level)
        visited.add(position)
        neighbors = set([position + direction
                         for direction in constants.DIRECTIONS_LIST])
        unvisited_neighbors = neighbors - visited
        unvisited_positions = unvisited_positions | unvisited_neighbors
        if(len(unvisited_neighbors) >= 1):
            position = random.sample(unvisited_neighbors, 1)[0]
        else:
            position = random.sample(unvisited_positions, 1)[0]
        while(not dungeon_level.has_tile(position)):
            position = random.sample(unvisited_positions, 1)[0]


class TileBrush(object):
    def __init__(self, shape, tile_modifier):
        self.shape = shape
        self.tile_modifier = tile_modifier

    def apply_brush(self, position, dungeon_level):
        for point in self.shape:
            dungeon_position = point + position
            self.tile_modifier.modify(dungeon_position, dungeon_level)


class SinglePointBrush(TileBrush):
    def __init__(self, tile_modifier):
        super(SinglePointBrush, self).__init__([vector2d.Vector2D(0, 0)],
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
