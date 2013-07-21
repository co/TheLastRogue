import terrain
import dungeonfeature
import entityscheduler
import settings
import tile
import turn
import player
import util
import geometry as geo
import constants
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
            unknown_terrain.replace_move((x, y), dungeon_level)
    return dungeon_level


def dungeon_level_from_file(file_name):
    terrain_matrix = terrain_matrix_from_file(file_name)
    dungeon_level = DungeonLevel(terrain_matrix, 1)
    set_terrain_from_file(dungeon_level, file_name)
    return dungeon_level


def terrain_matrix_from_file(file_name):
    dungeon = read_file(file_name)
    width = len(dungeon[0])
    height = len(dungeon)

    terrain_matrix = get_empty_tile_matrix(width, height)
    return terrain_matrix


def set_terrain_from_file(dungeon_level, file_name):
    dungeon = read_file(file_name)

    for x in range(dungeon_level.width):
        for y in range(dungeon_level.height):
            terrain = char_to_terrain(dungeon[y][x])
            terrain.replace_move((x, y), dungeon_level)


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
        self.entity_scheduler = entityscheduler.EntityScheduler()
        self.dungeon_features = []
        self.suspended_entity = None
        self.dungeon = None

        self.terrain_changed_timestamp = 0

        self.walkable_destinations = util.WalkableDestinatinationsPath()

    @property
    def entities(self):
        return self.entity_scheduler.entities

    def add_entity(self, entity):
        return self.entity_scheduler.register(entity)

    def remove_entity(self, entity):
        return self.entity_scheduler.release(entity)

    @property
    def up_stairs(self):
        return [feature for feature in self.dungeon_features
                if isinstance(feature, dungeonfeature.StairsUp)]

    @property
    def down_stairs(self):
        return [feature for feature in self.dungeon_features
                if isinstance(feature, dungeonfeature.StairsDown)]

    def draw_everything(self, camera):
        for y in range(settings.WINDOW_HEIGHT):
            for x in range(settings.WINDOW_WIDTH):
                position = (x, y)
                tile_position = geo.add_2d(position, camera.camera_offset)
                tile = self.get_tile_or_unknown(tile_position)
                tile.draw(position, True)

    def draw(self, camera):
        the_player = self._get_player_if_available()
        the_player.update_fov()
        for y in range(constants.GAME_STATE_HEIGHT):
            for x in range(constants.GAME_STATE_WIDTH):
                position = (x, y)
                self._draw_tile(camera, position, the_player)

    def _draw_tile(self, camera, position, the_player):
        tile_position = geo.add_2d(position, camera.camera_offset)
        screen_position = geo.add_2d(position, camera.screen_position)
        tile = self.get_tile_or_unknown(tile_position)
        x, y = tile_position
        if(libtcod.map_is_in_fov(the_player.dungeon_map, x, y)):
            the_player.update_memory_of_tile(tile, tile_position, self.depth)
            tile.draw(screen_position, True)
        else:
            player_memory_of_map = the_player.get_memory_of_map(self)
            player_memory_of_map.get_tile_or_unknown(tile_position).\
                draw(screen_position, False)

    def _get_player_if_available(self):
        return next((entity for entity in self.entities
                     if(isinstance(entity, player.Player))),
                    None)

    def add_dungeon_feature_if_not_present(self, new_dungeon_feature):
        if(not new_dungeon_feature in self.dungeon_features):
            self.dungeon_features.append(new_dungeon_feature)

    def remove_dungeon_feature_if_present(self, dungeon_feature_to_remove):
        if(dungeon_feature_to_remove in self.dungeon_features):
            self.dungeon_features.remove(dungeon_feature_to_remove)

    def add_entity_if_not_present(self, new_entity):
        if(not new_entity in self.entities):
            self.add_entity(new_entity)

    def remove_entity_if_present(self, entity_to_remove):
        if(entity_to_remove in self.entities):
            self.remove_entity(entity_to_remove)

    def has_tile(self, position):
        x, y = position
        return (0 <= y < len(self.tile_matrix) and
                0 <= x < len(self.tile_matrix[0]))

    def get_tile(self, position):
        x, y = position
        return self.tile_matrix[y][x]

    def get_tile_or_unknown(self, position):
        if(self.has_tile(position)):
            x, y = position
            return self.tile_matrix[y][x]
        else:
            return tile.unknown_tile

    def update(self):
        self.entity_scheduler.update_entities()
        self._remove_dead_monsters()

    def _remove_dead_monsters(self):
        for entity in self.entities:
            if(entity.is_dead()):
                entity.kill_and_remove()

    def signal_terrain_changed(self):
        self.terrain_changed_timestamp = turn.current_turn

    def print_dungeon(self):
        for y, row in enumerate(self.tile_matrix):
            line = ""
            for x, tile in enumerate(row):
                line += str(self.get_tile_or_unknown((x, y)).symbol)
            print line
