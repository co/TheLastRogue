import Terrain as terrain
import Tile as tile
import libtcodpy as libtcod
import copy


def unknown_level_map(width, height, depth):
    tile_matrix = [[terrain.Unknown()
                    for x in range(width)]
                   for y in range(height)]
    return DungeonLevel(tile_matrix, depth)


def test_dungeon_level():
    dungeon = read_file("test.level")
    width = len(dungeon[0])
    height = len(dungeon)

    depth = 0
    tile_matrix = [[char_to_tile(dungeon[y][x])
                    for x in range(width)]
                   for y in range(height)]
    return DungeonLevel(tile_matrix, depth)


def char_to_tile(c):
    if(c == '#'):
        return tile.Tile(terrain.Wall())
    elif(c == '+'):
        return tile.Tile(terrain.Door(False))
    elif(c == '~'):
        return tile.Tile(terrain.Water())
    elif(c == 'g'):
        return tile.Tile(terrain.GlassWall())
    else:
        return tile.Tile(terrain.Floor())


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
        self.__monsters = []

    def draw(self, player):
        self.update_calculate_dungeon_property_map(player)
        player.update_fov_map()
        player_memory_of_map = player.get_memory_of_map(self)
        for y, row in enumerate(self.tile_matrix):
            for x, tile in enumerate(row):
                if(libtcod.map_is_in_fov(player.fov_map, x, y)):
                    player.update_memory_of_tile(copy.deepcopy(tile),
                                                 x, y, self.depth)
                    tile.draw((x, y), True)
                else:
                    player_memory_of_map.tile_matrix[y][x].draw((x, y), False)

    def update(self, player):
        self.update_monsters(player)

    def update_monsters(self, player):
        for monster in self.__monsters:
            monster.update(self, player)

    def is_tile_empty_of_entity(self, position):
        if(self.tile_matrix[position.y][position.x].entity is None):
            return True
        return False

    def try_add_monster(self, monster):
        if((any(monster is m for m in self.__monsters)) or
           (not self.is_tile_empty_of_entity(monster.position))):
            return False

        self.__monsters.append(monster)
        new_pos = monster.position
        self.tile_matrix[new_pos.y][new_pos.x].entity = monster

    def is_tile_passable(self, position):
        return not self.tile_matrix[position.y][position.x].terrain.is_solid()

    def update_calculate_dungeon_property_map(self, player):
        player.fov_map = libtcod.map_new(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                terrain = self.tile_matrix[y][x].terrain
                libtcod.map_set_properties(player.fov_map, x, y,
                                           terrain.is_transparent(),
                                           terrain.is_solid())
