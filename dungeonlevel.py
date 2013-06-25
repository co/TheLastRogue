import terrain
import tile
import vector2d
import libtcodpy as libtcod


def unknown_level_map(width, height, depth):
    tile_matrix = [[tile.Tile(terrain.Unknown())
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
        self.__entities = []

    @property
    def entities(self):
        return self.__entities

    def draw(self, player, camera):
        self.update_calculate_dungeon_property_map(player)
        player.update_fov_map()
        player_memory_of_map = player.get_memory_of_map(self)
        for y, row in enumerate(self.tile_matrix):
            for x, current_tile in enumerate(row):
                position = vector2d.Vector2D(x, y)
                if(libtcod.map_is_in_fov(player.fov_map, x, y)):
                    player.update_memory_of_tile(current_tile,
                                                 position, self.depth)
                    current_tile.draw(position, True, camera)
                else:
                    player_memory_of_map.tile_matrix[y][x].draw(position,
                                                                False, camera)

    def add_entity_if_not_present(self, new_entity):
        if(not any(new_entity is entity for entity in self.entities)):
            self.__entities.append(new_entity)

    def remove_entity_if_present(self, entity_to_remove):
        if(any(entity_to_remove is entity for entity in self.entities)):
            self.__entities.remove(entity_to_remove)

    def update(self, player):
        self.update_entities(player)

    def put_item_on_tile(self, item, position):
        self.__entities[position.y][position.x].items.append(item)

    def update_entities(self, player):
        for entity in self.entities:
            entity.update(self, player)

    def update_calculate_dungeon_property_map(self, player):
        player.fov_map = libtcod.map_new(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                terrain = self.tile_matrix[y][x].terrain
                libtcod.map_set_properties(player.fov_map, x, y,
                                           terrain.is_transparent(),
                                           terrain.is_solid())
