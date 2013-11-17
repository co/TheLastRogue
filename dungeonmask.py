import colors
from compositecore import Leaf, CompositeMessage
from console import console
import geometry
import libtcodpy as libtcod
import turn


class DungeonMask(Leaf):
    """
    Holds the visibility mask and solidity mask of the entity
    """

    def __init__(self):
        super(DungeonMask, self).__init__()
        self.dungeon_map = None
        self.last_dungeon_map_update_timestamp = -1
        self.component_type = "dungeon_mask"

    def on_parent_changed(self):
        """
        A method hook called when the parent changes.
        """
        self.init_dungeon_map_if_has_dungeon_level()

    def init_dungeon_map_if_has_dungeon_level(self):
        """
        Initiates the dungeon map of a dungeon_level, if available.
        """
        if (self.has_sibling("dungeon_level") and
                not self.parent.dungeon_level.value is None):
            self._init_dungeon_map(self.parent.dungeon_level.value)
            self.last_dungeon_map_update_timestamp = -1

    def _init_dungeon_map(self, dungeon_level):
        """
        Initiates the dungeon map of a dungeon_level.
        """
        self.dungeon_map = libtcod.map_new(dungeon_level.width,
                                           dungeon_level.height)

    def can_see_point(self, point):
        """
        Checks if a particular point is visible to this entity.

        Args:
            point (int, int): The point to check.
        """
        x, y = point
        return libtcod.map_is_in_fov(self.dungeon_map, x, y)

    def update_fov(self):
        """
        Calculates the Field of Vision from the dungeon_map.
        """
        x, y = self.parent.position.value
        sight_radius = self.parent.sight_radius.value
        libtcod.map_compute_fov(self.dungeon_map, x, y,
                                sight_radius, True)

    def print_walkable_map(self):
        """
        Prints a map of where this entity is allowed to walk.
        """
        for y in range(libtcod.map_get_height(self.dungeon_map)):
            line = ""
            for x in range(libtcod.map_get_width(self.dungeon_map)):
                if (libtcod.map_is_walkable(self.dungeon_map, x, y)):
                    line += " "
                else:
                    line += "#"
            print(line)

    def print_is_transparent_map(self):
        """
        Prints a map of what this entity can see through.
        """
        for y in range(libtcod.map_get_height(self.dungeon_map)):
            line = ""
            for x in range(libtcod.map_get_width(self.dungeon_map)):
                if libtcod.map_is_transparent(self.dungeon_map, x, y):
                    line += " "
                else:
                    line += "#"
            print(line)

    def print_visible_map(self):
        """
        Prints a map of what this entity sees right now.
        """
        for y in range(libtcod.map_get_height(self.dungeon_map)):
            line = ""
            for x in range(libtcod.map_get_width(self.dungeon_map)):
                if libtcod.map_is_in_fov(self.dungeon_map, x, y):
                    line += " "
                else:
                    line += "#"
            print(line)

    def before_tick(self, time):
        self.update_dungeon_map_if_its_old()

    def update_dungeon_map_if_its_old(self):
        """
        Updates the dungeon map it is older than the latest change.
        """
        dungeon_level = self.parent.dungeon_level.value
        if (dungeon_level.terrain_changed_timestamp >
                self.last_dungeon_map_update_timestamp):
            self.update_dungeon_map()

    def update_dungeon_map(self):
        """
        Updates the dungeon map.
        """
        dungeon_level = self.parent.dungeon_level.value
        for y in range(dungeon_level.height):
            for x in range(dungeon_level.width):
                terrain = \
                    dungeon_level.get_tile_or_unknown((x, y)).get_terrain()
                libtcod.map_set_properties(self.dungeon_map, x, y,
                                           terrain.is_transparent.value,
                                           self.parent.
                                           mover.can_pass_terrain(terrain))
        self.last_dungeon_map_update_timestamp = turn.current_turn
        self.update_fov()

    def message(self, message):
        """
        Handles recieved messages.
        """
        if message == CompositeMessage.DUNGEON_LEVEL_CHANGED:
            self.init_dungeon_map_if_has_dungeon_level()


class Path(Leaf):
    """
    Composites holding this has a path that it may step through.
    """

    def __init__(self):
        super(Path, self).__init__()
        self._path = None
        self.path = []
        self.component_type = "path"

    def init_path(self):
        """
        Initiates the path using the dungeon map, from the DungeonMask module.
        """
        dungeon_map = self.parent.dungeon_mask.dungeon_map
        self._path = libtcod.path_new_using_map(dungeon_map, 1.0)

    def has_path(self):
        """
        Returns True if the entity has a path to walk.
        """
        if len(self.path) > 0:
            return True
        return False

    def try_step_path(self):
        """
        Tries to step the entity along the path, relies on the mover module.
        """
        if not self.has_path():
            return False
        next_point = self.path.pop()
        if not geometry.chess_distance(next_point, self.parent.position.value) == 1:
            print "set_line", next_point, self.parent.position.value
            self.set_line_path(next_point)
        step_succeeded = self.parent.mover.try_move_or_bump(next_point)
        if not step_succeeded:
            print "remove path"
            self.clear()
        return step_succeeded

    def compute_path(self, destination):
        sx, sy = self.parent.position.value
        dx, dy = destination
        libtcod.path_compute(self._path, sx, sy, dx, dy)
        self.clear()
        x, y = libtcod.path_walk(self._path, True)
        while not x is None:
            self.path.insert(0, (x, y))
            x, y = libtcod.path_walk(self._path, True)

    def set_line_path(self, destination):
        sx, sy = self.parent.position.value
        dx, dy = destination
        libtcod.line_init(sx, sy, dx, dy)
        self.clear()
        x, y = libtcod.line_step()
        while not x is None:
            self.path.insert(0, (x, y))
            x, y = libtcod.line_step()

    def clear(self):
        self.path = []

    def draw(self, camera):
        points = list(self.path)
        points.reverse()
        for point in points:
            if not self.parent.mover.can_pass_terrain(
                    self.parent.dungeon_level.value.get_tile_or_unknown(point).get_terrain()):
                break
            console.set_symbol(camera.dungeon_to_screen_position(point), ":")
            console.set_color_fg(camera.dungeon_to_screen_position(point), colors.WHITE)

    def message(self, message):
        if message == CompositeMessage.DUNGEON_LEVEL_CHANGED:
            self.init_path()
