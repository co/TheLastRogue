import Terrain as terrain
import libtcodpy as libtcod


def unknown_level_map(width, height, depth):
    tile_matrix = [[terrain.Unknown((x, y))
                    for x in range(width)]
                   for y in range(height)]
    return DungeonLevel(tile_matrix, depth)


def test_dungeon_level():
    dungeon = read_file("test.level")
    width = len(dungeon[0])
    height = len(dungeon)

    depth = 0
    tile_matrix = [[char_to_terrain(dungeon[y][x], (x, y))
                    for x in range(width)]
                   for y in range(height)]
    return DungeonLevel(tile_matrix, depth)


def char_to_terrain(c, position):
    if(c == '#'):
        return terrain.Wall(position)
    elif(c == '+'):
        return terrain.Door(position, False)
    elif(c == '~'):
        return terrain.Water(position)
    elif(c == ' '):
        return terrain.Floor(position)


def read_file(file_name):
    f = open(file_name, "r")
    data = f.readlines()
    data = [line.strip() for line in data]
    f.close()
    return data


class DungeonLevel(object):

    def __init__(self, tile_matrix, depth):
        self.height = len(tile_matrix)
        self.width = len(tile_matrix[0])
        self.tile_matrix = tile_matrix
        self.depth = depth

    def draw(self, player):
        self.update_calculate_dungeon_property_map(player)
        player.update_fov_map()
        player_memory_of_map = player.get_memory_of_map(self)
        for y, row in enumerate(self.tile_matrix):
            for x, tile in enumerate(row):
                if(libtcod.map_is_in_fov(player.fov_map, x, y)):
                    player.update_memory_of_tile(tile, x, y, self.depth)
                    tile.draw(True)
                else:
                    player_memory_of_map.tile_matrix[y][x].draw(False)

    def is_tile_passable(self, position):
        return not self.tile_matrix[position.y][position.x].is_solid()

    def update_calculate_dungeon_property_map(self, player):
        player.fov_map = libtcod.map_new(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tile_matrix[y][x]
                libtcod.map_set_properties(player.fov_map, x, y,
                                           tile.is_transparent(),
                                           tile.is_solid())
