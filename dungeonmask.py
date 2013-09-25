from compositecore import Leaf
from sightradius import SightRadius
import libtcodpy as libtcod
import turn


class DungeonMask(Leaf):
    """
    Holds the visibility mask and solidity mask of the entity
    """
    def __init__(self, arg):
        super(DungeonMask, self).__init__()
        self.dungeon_map
        self.last_dungeon_map_update_timestamp = -1

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
        Calculates the Field of Visuon from the dungeon_map.
        """
        x, y = self.position
        sight_radius = self.get_sibling_of_type(SightRadius).sight_radius
        libtcod.map_compute_fov(self.dungeon_map, x, y,
                                sight_radius, True)

    def print_walkable_map(self):
        """
        Prints a map of where this entity is allowed to walk.
        """
        for y in range(libtcod.map_get_height(self.dungeon_map)):
            line = ""
            for x in range(libtcod.map_get_width(self.dungeon_map)):
                if(libtcod.map_is_walkable(self.dungeon_map, x, y)):
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
                if(libtcod.map_is_transparent(self.dungeon_map, x, y)):
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
                if(libtcod.map_is_in_fov(self.dungeon_map, x, y)):
                    line += " "
                else:
                    line += "#"
            print(line)

    def update_dungeon_map_if_its_old(self):
        """
        Updates the dungeon map it is older than the latest change.
        """
        if(self.dungeon_level.terrain_changed_timestamp >
           self.last_dungeon_map_update_timestamp):
            self.update_dungeon_map()

    def update_dungeon_map(self):
        """
        Updates the dungeon map.
        """
        for y in range(self.dungeon_level.height):
            for x in range(self.dungeon_level.width):
                terrain = self.dungeon_level.tile_matrix[y][x].get_terrain()
                libtcod.map_set_properties(self.dungeon_map, x, y,
                                           terrain.is_transparent(),
                                           self._can_pass_terrain(terrain))
        self.last_dungeon_map_update_timestamp = turn.current_turn
        self.update_fov()
