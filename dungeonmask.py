import colors
from compositecore import Leaf, CompositeMessage
from console import console
import geometry
import icon
import libtcodpy as libtcod
import turn


class DungeonMask(Leaf):
    """
    Holds the visibility mask and solidity mask of the entity
    """

    def __init__(self):
        super(DungeonMask, self).__init__()
        self._dungeon_map = None
        self.last_dungeon_map_update_timestamp = -1
        self.last_sight_radius = -1
        self.component_type = "dungeon_mask"

    @property
    def dungeon_map(self):
        if self._dungeon_map is None:
            self.init_dungeon_map_if_has_dungeon_level()
        return self._dungeon_map

    @dungeon_map.setter
    def dungeon_map(self, value):
        self._dungeon_map = value

    def __getstate__(self):
        state = dict(self.__dict__)
        del state["_dungeon_map"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.last_dungeon_map_update_timestamp = -1
        self.dungeon_map = None

    def init_dungeon_map_if_has_dungeon_level(self):
        """
        Initiates the dungeon map of a dungeon_level, if available.
        """
        if (self.has_sibling("dungeon_level") and
                not self.parent.dungeon_level.value is None):
            self._init_dungeon_map()
            self.last_dungeon_map_update_timestamp = -1

    def _init_dungeon_map(self):
        """
        Initiates the dungeon map of a dungeon_level.
        """
        self.dungeon_map = libtcod.map_new(self.parent.dungeon_level.value.width,
                                           self.parent.dungeon_level.value.height)

    def can_see_point(self, point):
        """
        Checks if a particular point is visible to this entity.

        Args:
            point (int, int): The point to check.
        """
        x, y = point
        return libtcod.map_is_in_fov(self.dungeon_map, x, y)

    def on_tick(self, _):
        sight_radius = self.parent.sight_radius.value
        if not self.last_sight_radius == sight_radius:
            self.update_fov()

    def update_fov(self):
        """
        Calculates the Field of Vision from the dungeon_map.
        """
        x, y = self.parent.position.value
        sight_radius = self.parent.sight_radius.value
        libtcod.map_compute_fov(self.dungeon_map, x, y,
                                sight_radius, True)
        self.last_sight_radius = sight_radius

    def print_walkable_map(self):
        """
        Prints a map of where this entity is allowed to walk.
        """
        for y in range(libtcod.map_get_height(self.dungeon_map)):
            line = ""
            for x in range(libtcod.map_get_width(self.dungeon_map)):
                if libtcod.map_is_walkable(self.dungeon_map, x, y):
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
        Handles received messages.
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
        self.position_list = []
        self.component_type = "path"

    def __getstate__(self):
        state = dict(self.__dict__)
        del state["_path"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._path = None

    @property
    def path(self):
        if self._path is None:
            self.init_path()
        return self._path

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
        if len(self.position_list) > 0:
            return True
        return False

    def try_step_path(self):
        """
        Tries to step the entity along the path, relies on the mover module.
        """
        if not self.has_path():
            return False
        next_point = self.position_list.pop()
        if not geometry.chess_distance(next_point, self.parent.position.value) == 1:
            self.set_line_path(next_point)
        energy_spent = self.parent.stepper.try_move_or_bump(next_point)
        if energy_spent <= 0:
            self.clear()
        return energy_spent

    def compute_path(self, destination):
        sx, sy = self.parent.position.value
        dx, dy = destination
        libtcod.path_compute(self.path, sx, sy, dx, dy)
        self.clear()
        x, y = libtcod.path_walk(self.path, True)
        while not x is None:
            self.position_list.insert(0, (x, y))
            x, y = libtcod.path_walk(self.path, True)

    def set_line_path(self, destination):
        sx, sy = self.parent.position.value
        dx, dy = destination
        libtcod.line_init(sx, sy, dx, dy)
        self.clear()
        x, y = libtcod.line_step()
        while not x is None:
            self.position_list.insert(0, (x, y))
            x, y = libtcod.line_step()

    def clear(self):
        self.position_list = []

    def draw(self, camera):
        points = list(self.position_list)
        points.reverse()
        for point in points:
            if not self.parent.mover.can_pass_terrain(
                    self.parent.dungeon_level.value.get_tile_or_unknown(point).get_terrain()):
                break
            console.set_symbol(camera.dungeon_to_screen_position(point), icon.FOOT_STEPS)
            console.set_color_fg(camera.dungeon_to_screen_position(point), colors.GRAY)

    def message(self, message):
        if message == CompositeMessage.DUNGEON_LEVEL_CHANGED:
            self.init_path()
