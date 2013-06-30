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
        self.entities = []
        self.dungeon_map = libtcod.map_new(self.width, self.height)
        self._update_dungeon_map()

    def draw(self, player, camera):
        player.update_fov()
        player_memory_of_map = player.get_memory_of_map(self)
        for y, row in enumerate(self.tile_matrix):
            for x, current_tile in enumerate(row):
                position = vector2d.Vector2D(x, y)
                if(libtcod.map_is_in_fov(player.dungeon_map, x, y)):
                    player.update_memory_of_tile(current_tile,
                                                 position, self.depth)
                    current_tile.draw(position, True, camera)
                else:
                    player_memory_of_map.tile_matrix[y][x].draw(position,
                                                                False, camera)

    def add_entity_if_not_present(self, new_entity):
        if(not any(new_entity is entity for entity in self.entities)):
            self.entities.append(new_entity)

    def put_item_on_tile(self, item, position):
        self.get_tile(position).items.append(item)

    def remove_entity_if_present(self, entity_to_remove):
        if(any(entity_to_remove is entity for entity in self.entities)):
            self.entities.remove(entity_to_remove)
            return True
        return False

    def get_tile(self, position):
        return self.tile_matrix[position.y][position.x]

    def update(self, player):
        self._entities_calculate_fov()
        self._entities_act(player)
        self._entities_effects_update()
        self._remove_dead_monsters()

    def _entities_calculate_fov(self):
        self._update_dungeon_map()
        for entity in self.entities:
            libtcod.map_copy(self.dungeon_map, entity.dungeon_map)
            entity.update_fov()

    def _update_dungeon_map(self):
        for y in range(self.height):
            for x in range(self.width):
                terrain = self.tile_matrix[y][x].terrain
                libtcod.map_set_properties(self.dungeon_map, x, y,
                                           terrain.is_transparent(),
                                           not terrain.is_solid())

    def print_is_transparent_map(self):
        print libtcod.map_get_height(self.dungeon_map)
        for y in range(libtcod.map_get_height(self.dungeon_map)):
            line = ""
            for x in range(libtcod.map_get_width(self.dungeon_map)):
                if(libtcod.map_is_transparent(self.dungeon_map, x, y)):
                    line += " "
                else:
                    line += "#"
            print(line)

    def _entities_effects_update(self):
        for entity in self.entities:
            entity.update_effect_queue()

    def _entities_act(self, player):
        for entity in self.entities:
            if(not entity.is_dead()):
                entity.update(player)

    def _remove_dead_monsters(self):
        for entity in self.entities:
            if(entity.is_dead()):
                entity.kill()
