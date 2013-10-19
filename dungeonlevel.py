import direction
import dungeonfeature
import actionscheduler
import settings
import turn
import util
import geometry as geo
import constants
import libtcodpy as libtcod
import tile


class DungeonLevel(object):
    def __init__(self, tile_matrix, depth):
        self.height = len(tile_matrix)
        self.width = len(tile_matrix[0])
        self.tile_matrix = tile_matrix
        self.depth = depth
        self.actor_scheduler = actionscheduler.ActionScheduler()
        self.dungeon_features = []
        self.dungeon = None

        self.terrain_changed_timestamp = 0

        self.walkable_destinations = util.WalkableDestinatinationsPath()

    @property
    def entities(self):
        return self.actor_scheduler.entities

    @property
    def actors(self):
        return self.actor_scheduler.actors

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
                the_tile = self.get_tile_or_unknown(tile_position)
                the_tile.draw(position, True)

    def draw(self, camera):
        the_player = self._get_player_if_available()
        if(the_player is None):
            raise Exception(("Tried to access the player, "
                             "from DungeonLevel: " + str(self) +
                             ", but the player is not in the dungeon."))
        for y in range(constants.GAME_STATE_HEIGHT):
            for x in range(constants.GAME_STATE_WIDTH):
                position = (x, y)
                self._draw_tile(camera, position, the_player)

    def _draw_tile(self, camera, position, the_player):
        tile_position = geo.add_2d(position, camera.camera_offset)
        screen_position = geo.add_2d(position, camera.screen_position)
        the_tile = self.get_tile_or_unknown(tile_position)
        x, y = tile_position
        dungeon_mask = the_player.dungeon_mask
        dungeon_mask.update_fov()
        dungeon_map = the_player.dungeon_mask.dungeon_map
        memory_map = the_player.memory_map
        if(libtcod.map_is_in_fov(dungeon_map, x, y)):
            memory_map.update_memory_of_tile(the_tile, tile_position,
                                             self.depth)
            the_tile.draw(screen_position, True)
        else:
            player_memory_of_map = memory_map.get_memory_of_map(self)
            player_memory_of_map.get_tile_or_unknown(tile_position).\
                draw(screen_position, False)

    def _get_player_if_available(self):
        return next((entity for entity in self.entities
                    if entity.has_child("is_player")), None)

    def add_dungeon_feature_if_not_present(self, new_dungeon_feature):
        if(not new_dungeon_feature in self.dungeon_features):
            self.dungeon_features.append(new_dungeon_feature)

    def remove_dungeon_feature_if_present(self, dungeon_feature_to_remove):
        if(dungeon_feature_to_remove in self.dungeon_features):
            self.dungeon_features.remove(dungeon_feature_to_remove)

    def add_actor_if_not_present(self, new_actor):
        if(not new_actor in self.actors):
            self._add_actor(new_actor)

    def remove_actor_if_present(self, actor_to_remove):
        if(actor_to_remove in self.actors):
            self._remove_actor(actor_to_remove)

    def _add_actor(self, actor):
        return self.actor_scheduler.register(actor)

    def _remove_actor(self, actor):
        return self.actor_scheduler.release(actor)

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

    def get_tiles_surrounding_position(self, position):
        return [self.get_tile_or_unknown(geo.add_2d(offset, position))
                for offset in direction.AXIS_DIRECTIONS]

    def tick(self):
        self.actor_scheduler.tick()
        self._remove_dead_monsters()

    def _remove_dead_monsters(self):
        for entity in self.entities:
            if(entity.health.is_dead()):
                entity.kill_and_remove()

    def signal_terrain_changed(self):
        self.terrain_changed_timestamp = turn.current_turn

    def print_dungeon(self):
        for y, row in enumerate(self.tile_matrix):
            line = ""
            for x, tile in enumerate(row):
                line += str(self.get_tile_or_unknown((x, y)).symbol)
            print line

    def get_walkable_positions(self):
        return (self.walkable_destinations
                .get_walkable_positions(self.parent,
                                        self.parent.position.value))
