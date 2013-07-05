import terrain
import constants
import tile
import turn
import vector2d
import libtcodpy as libtcod


def get_empty_tile_matrix(width, height):
    return [[tile.Tile()
             for x in range(width)]
            for y in range(height)]


def unknown_level_map(width, height, depth):
    tile_matrix = get_empty_tile_matrix(width, height)
    dungeon_level = DungeonLevel(tile_matrix, depth)
    for x in range(width):
        for y in range(height):
            unknown_terrain = terrain.Unknown()
            unknown_terrain.replace_move(vector2d.Vector2D(x, y),
                                         dungeon_level)
    return dungeon_level


def dungeon_level_from_file(file_name):
    terrain_matrix = terrain_matrix_from_file(file_name)
    dungeon_level = DungeonLevel(terrain_matrix, 1)
    set_terrain_from_file(dungeon_level, file_name)
    return dungeon_level


def terrain_matrix_from_file(file_name):
    dungeon = read_file("test.level")
    width = len(dungeon[0])
    height = len(dungeon)

    terrain_matrix = get_empty_tile_matrix(width, height)
    return terrain_matrix


def set_terrain_from_file(dungeon_level, file_name):
    dungeon = read_file("test.level")

    for x in range(dungeon_level.width):
        for y in range(dungeon_level.height):
            terrain = char_to_terrain(dungeon[y][x])
            terrain.replace_move(vector2d.Vector2D(x, y), dungeon_level)


def char_to_terrain(c):
    if(c == '#'):
        return terrain.Wall()
    elif(c == '+'):
        return terrain.Door(False)
    elif(c == '~'):
        return terrain.Water()
    elif(c == 'g'):
        return terrain.GlassWall()
    else:
        return terrain.Floor()


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
        self.suspended_entity = None
        self._walkable_positions_dictionary_cache = {}
        self._walkable_positions_cache_timestamp = -1
        self._terrain_changed_timestamp = 0

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
        self._entities_clear_status()
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
                terrain = self.tile_matrix[y][x].get_terrain()
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
            if(not(self.suspended_entity is None or
               entity is self.suspended_entity)):
                continue
            if(not entity.is_dead()):
                done = entity.update(player)
                if not done:
                    self.suspended_entity = entity
                    break
                else:
                    self.suspended_entity = None

    def _entities_clear_status(self):
        for entity in self.entities:
            entity.clear_all_status()

    def _remove_dead_monsters(self):
        for entity in self.entities:
            if(entity.is_dead()):
                entity.kill()

    def get_walkable_positions_from_start_position(self, position):
        if(not (position in self._walkable_positions_dictionary_cache.keys()
                and self._terrain_changed_timestamp <=
                self._walkable_positions_cache_timestamp)):
            self._calculate_walkable_positions_from_start_position(position)
        return self._walkable_positions_dictionary_cache[position]

    def _calculate_walkable_positions_from_start_position(self, position):
        visited = set()
        visited.add(position)
        queue = [position]
        queue.extend(self._get_walkable_neighbors(position))
        while (len(queue) > 0):
            position = queue.pop()
            while(len(queue) > 0 and position in visited):
                position = queue.pop()
            visited.add(position)
            neighbors = set(self._get_walkable_neighbors(position)) - visited
            queue.extend(neighbors)
        visited = list(visited)
        for point in visited:
            self._walkable_positions_dictionary_cache[point] = visited
        self._walkable_positions_cache_timestamp = turn.current_turn

    def _get_walkable_neighbors(self, position):
        result_positions = []
        for direction in constants.DIRECTIONS.values():
            neighbor_position = position + direction
            x, y = neighbor_position.x, neighbor_position.y
            try:
                neighbor = self.tile_matrix[y][x]
                if(not neighbor.get_terrain().is_solid()):
                    result_positions.append(neighbor_position)
            except IndexError:
                pass
        return result_positions
