import colors
from console import console
import direction
import dungeonfeature
import actionscheduler
import libtcodpy
import settings
import turn
import util
import geometry as geo
import constants
import tile


class DungeonLevel(object):
    def __init__(self, tile_matrix, depth):
        self.width = len(tile_matrix[0])
        self.height = len(tile_matrix)
        self._dungeon_level_screen = DungeonLevelScreen(self)
        self.tile_matrix = tile_matrix
        self.depth = depth
        self.actor_scheduler = actionscheduler.ActionScheduler()
        self.dungeon_features = []
        self.dungeon = None
        self.terrain_changed_timestamp = 0

        self._walkable_destinations = util.WalkableDestinatinationsPath()

        self.x = 0

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

    def draw_everything(self, camera):
        self._dungeon_level_screen.draw_everything(camera, self.tile_matrix)
        self._dungeon_level_screen.blit(camera.offset)

    def draw_close_to_player(self, camera):
        the_player = self._get_player_if_available()
        if the_player is None:
            raise Exception(("Tried to access the player, "
                             "from DungeonLevel: " + str(self) +
                             ", but the player is not in the dungeon."))
        square_side = 16  # Should be enough
        rect_pos = geo.sub_2d(the_player.position.value, (square_side / 2, square_side / 2))
        draw_rectangle = geo.Rect(rect_pos, square_side, square_side)
        self._dungeon_level_screen.draw_rectangle_seen_by_entity(draw_rectangle, self.tile_matrix, the_player)
        self._dungeon_level_screen.blit(camera.offset)

    def draw_all_within_screen(self, camera):
        the_player = self._get_player_if_available()
        if the_player is None:
            raise Exception(("Tried to access the player, "
                             "from DungeonLevel: " + str(self) +
                             ", but the player is not in the dungeon."))
        self._dungeon_level_screen.redraw_screen_as_seen_by_entity(self.tile_matrix, the_player)
        self._dungeon_level_screen.blit(camera.offset)

    @property
    def down_stairs(self):
        return [feature for feature in self.dungeon_features
                if isinstance(feature, dungeonfeature.StairsDown)]

    def _get_player_if_available(self):
        return next((entity for entity in self.entities
                     if entity.has_child("is_player")), None)

    def add_dungeon_feature_if_not_present(self, new_dungeon_feature):
        if not new_dungeon_feature in self.dungeon_features:
            self.dungeon_features.append(new_dungeon_feature)

    def remove_dungeon_feature_if_present(self, dungeon_feature_to_remove):
        if dungeon_feature_to_remove in self.dungeon_features:
            self.dungeon_features.remove(dungeon_feature_to_remove)

    def add_actor_if_not_present(self, new_actor):
        if not new_actor in self.actors:
            self._add_actor(new_actor)

    def remove_actor_if_present(self, actor_to_remove):
        if actor_to_remove in self.actors:
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
        return get_tile_or_unknown(position, self.tile_matrix)

    def get_tiles_surrounding_position(self, position):
        return [self.get_tile_or_unknown(geo.add_2d(offset, position))
                for offset in direction.AXIS_DIRECTIONS]

    def tick(self):
        self.actor_scheduler.tick()
        self._remove_dead_monsters()

    def _remove_dead_monsters(self):
        dead_entities = [entity for entity in self.entities if entity.health.is_dead()]
        for entity in dead_entities:
            entity.on_death_action.act()

    def signal_terrain_changed(self):
        self.terrain_changed_timestamp = turn.current_turn

    def print_dungeon(self):
        for y, row in enumerate(self.tile_matrix):
            line = ""
            for x, tile in enumerate(row):
                line += str(self.get_tile_or_unknown((x, y)).icon)
            print(line)

    def get_walkable_positions(self, entity, position):
        return (self._walkable_destinations
                .get_walkable_positions(entity, position))


class DungeonLevelScreen(object):
    def __init__(self, dungeon_level):
        self.dungeon_level = dungeon_level
        self._console = None

    @property
    def console(self):
        if self._console is None:
            self._console = libtcodpy.console_new(max(self.dungeon_level.width, constants.GAME_STATE_WIDTH),
                                                  max(self.dungeon_level.height, constants.GAME_STATE_HEIGHT))
        return self._console

    def __getstate__(self):
        state = dict(self.__dict__)
        del state["_console"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._console = None

    def draw_everything(self, camera, tile_matrix):
        for y in range(settings.WINDOW_HEIGHT):
            for x in range(settings.WINDOW_WIDTH):
                position = (x, y)
                tile_position = geo.add_2d(position, camera.camera_offset)
                the_tile = get_tile_or_unknown(tile_position, tile_matrix)
                the_tile.draw(self.console, position, True)

    def draw_rectangle_seen_by_entity(self, rectangle, tile_matrix, entity):
        for y in range(rectangle.top, rectangle.bottom):
            for x in range(rectangle.left, rectangle.right):
                position = (x, y)
                self._draw_tile(position, tile_matrix, entity)

    def redraw_screen_as_seen_by_entity(self, tile_matrix, entity):
        for y in range(constants.GAME_STATE_HEIGHT):
            for x in range(constants.GAME_STATE_WIDTH):
                position = (x, y)
                self._draw_tile(position, tile_matrix, entity)

    def _draw_tile(self, position, tile_matrix, entity):
        if entity.dungeon_mask.can_see_point(position):
            the_tile = get_tile_or_unknown(position, tile_matrix)
            entity.memory_map.update_memory_of_tile(the_tile, position, self.dungeon_level.depth)
            the_tile.draw(self.console, position, True)
        else:
            the_tile = entity.memory_map.get_memory_of_map(self.dungeon_level).get_tile_or_unknown(position)
            the_tile.draw(self.console, position, False)

    def blit(self, source_position):
        src_x, src_y = source_position
        libtcodpy.console_blit(self.console, src_x, src_y, constants.GAME_STATE_WIDTH, constants.GAME_STATE_HEIGHT, 0,
                               0, 0)


def get_tile_or_unknown(position, tile_matrix):
    x, y = position
    if x < 0 or y < 0:
        return tile.unknown_tile
    try:
        return tile_matrix[y][x]
    except IndexError:
        return tile.unknown_tile

