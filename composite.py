import counter
import turn
import libtcodpy as libtcod
import gametime
import colors
import symbol
import console


class Component(object):
    """
    Abstract base class of composite design pattern.

    New classes should not inherit from this class but from
    the Leaf or Composite classes instead.

    Attributes:
        parent (Component): The parent component.
        Is None if this is a root component.
    """
    def __init__(self, *args, **kw):
        self.parent = None
        pass

    def precondition(self, *args, **kw):
        """
        A method hook for checking if it's valid to update all components.
        """
        return True

    def update(self, *args, **kw):
        """
        A method hook for updating the component tree.
        """
        pass

    def get_sibling_of_type(self, component_type):
        """
        Gets the first child of the parent which is of the given type.
        """
        return self.parent.get_child_of_type(component_type)

    def has_sibling(self, component_type):
        """
        Returns true if this components parent has a child of the given type.

        False otherwise.
        """
        return self.parent.has_child(component_type)


class Leaf(Component):
    """
    Abstract leaf class of composite design pattern.

    Component classes of leaf type should inherit from this class.
    """
    def __init__(self, *args, **kw):
        super(Leaf, self).__init__(*args, **kw)


class Composite(Component):
    """
    Abstract composite class of composite design pattern.

    Component classes of composite type should inherit from this class.
    Composite objects may hold other Components.
    """
    def __init__(self, *args, **kw):
        super(Composite, self).__init__(*args, **kw)
        self.children = []

    def add_child(self, child):
        """
        Adds a child component to this component.
        If the child already has a parent an exception is thrown.
        """
        self.children.append(child)
        if(not child.parent is None):
            print """Component {0} tried ta add_child
                     component: {1} to its children.
                     But it already
                     had parent: {2}.""".format(str(self),
                                                str(child),
                                                str(child.parent))
            raise
        child.parent = self

    def remove_child_of_type(self, child_type):
        """
        Removes a child component to this component.
        """
        child = self.get_child_of_type(child_type)
        self.children.remove(child)
        child.parent = None

    def update(self):
        """
        Runs update on all child components.
        """
        map(lambda x: x.update(), self.children)

    def get_child_of_type(self, component_type):
        """
        Gets the first child which is of the given type.
        """
        if self.has_child(component_type):
            return next(child for child in self.children
                        if isinstance(child, component_type))
        else:
            return None

    def has_child(self, component_type):
        """
        Returns true if this component has a child of the given type.

        False otherwise.
        """
        return any(isinstance(child, component_type)
                   for child in self.children)


class Player(Composite):
    """
    A composite component representing the player character.
    """
    def __init__(self):
        super(Player, self).__init__()
        self.add_child(Position())
        self.add_child(DungeonLevel())
        self.add_child(Description())
        self.add_child(GraphicChar(symbol.GUNSLINGER_THIN,
                                   None, colors.WHITE))

        self.add_child(Health(10))
        self.add_child(Strength(10))
        self.add_child(MovementSpeed(gametime.single_turn))
        self.add_child(AttackSpeed(gametime.single_turn))
        self.add_child(Faction(Faction.Player))
        self.add_child(SightRadius(6))
        self.add_child(StatusFlags(6))
        self.add_child(Inventory(6))
        #self.add_child(equipment.Equipment(6))

### EffectQueue # Use Clausen style stuff.
### StatusFlags
### GameState???
### GamePiece
### DungeonMap


class Actor(Leaf):
    """
    An abstract component, enteties with this component can act.
    """
    def __init__(self):
        super(Actor, self).__init__()

    def act(self):
        """
        The action the parent component should do. And return energy spent.

        Subclasses should override this method.
        """
        pass


class GamePieceType(Leaf):
    ENTITY = 0
    CLOUD = 1
    ITEM = 2
    DUNGEON_FEATURE = 3
    DUNGEON_TRASH = 4
    TERRAIN = 5

    _MAX_INSTANCES_OF_PIECE_TYPE_ON_TILE = {ENTITY: 1,
                                            CLOUD: 1,
                                            ITEM: 1,
                                            DUNGEON_FEATURE: 1,
                                            DUNGEON_TRASH: 1,
                                            TERRAIN: 1}

    def __init__(self, piece_type=None):
        super(GamePieceType, self).__init__()
        self.value = piece_type

    @property
    def max_instances_in_tile(self):
        return self.__class__.\
            _MAX_INSTANCES_OF_PIECE_TYPE_ON_TILE[self.value]


class KeyboardEventMover(Leaf):
    """
    Composites holding this has a position in the dungeon.
    """

    def __init__(self):
        super(KeyboardEventMover, self).__init__()
        self._status_flags = set()

    def has_status(self, status):
        return status in self._status_flags


class StatusFlags(Leaf):
    """
    Composites holding this has status flags, describing their behaviour.
    """
    INVISIBILE = 0
    SEE_INVISIBILITY = 1
    FLYING = 2
    HAS_MIND = 3
    CAN_OPEN_DOORS = 4
    SWALLOWED_BY_SLIME = 5
    LEAVES_CORPSE = 6

    def __init__(self):
        super(StatusFlags, self).__init__()
        self._status_flags = set()

    def has_status(self, status):
        return status in self._status_flags

    def add_status(self, status):
        return self._status_flags.add(status)


class Position(Leaf):
    """
    Composites holding this has a position in the dungeon.
    """
    def __init__(self):
        super(Position, self).__init__()
        self.position = (-1, -1)


class DungeonLevel(Leaf):
    """
    Composites holding this has a position in the dungeon.
    """
    def __init__(self):
        super(DungeonLevel, self).__init__()
        self._dungeon_level = None

    @property
    def dungeon_level(self):
        """
        Gets the dungeon_level the entity is currently in.
        """
        return self._dungeon_level

    @dungeon_level.setter
    def dungeon_level(self, value):
        """
        Sets current dungeon_level of the entity.
        Also updates the visibility/solidity of the dungeon_level tiles.
        """
        if((not self.dungeon_level is value) and (not value is None)):
            self._dungeon_level = value
            dungeon_mask_module = self.get_sibling_of_type(DungeonMask)
            dungeon_mask_module.dungeon_map = libtcod.map_new(value.width,
                                                              value.height)
            dungeon_mask_module.update_dungeon_map()
            self.path = libtcod.path_new_using_map(self.dungeon_map, 1.0)
            if(self.has_sibling(MemmoryMap)):
                self.get_sibling_of_type(MemmoryMap).\
                    set_memory_map_if_not_set(self.dungeon_level)


class MemmoryMap(Leaf):
    """
    Composites holding this has a position in the dungeon.
    """
    def __init__(self):
        super(MemmoryMap, self).__init__()
        self.position = (-1, -1)
        self.depth = -1


class Strength(Leaf):
    """
    Composites holding this has the strength attribute.
    """
    def __init__(self, strength):
        super(Strength, self).__init__()
        self.strength = strength


class AttackSpeed(Leaf):
    """
    Composites holding this has the attack_speed attribute.
    """
    def __init__(self, attack_speed):
        super(AttackSpeed, self).__init__()
        self.attack_speed = attack_speed


class MovementSpeed(Leaf):
    """
    Composites holding this has the attack_speed attribute.
    """
    def __init__(self, attack_speed):
        super(MovementSpeed, self).__init__()
        self.attack_speed = attack_speed


class SightRadius(Leaf):
    """
    Composites holding this has the sight_radius attribute.
    """
    def __init__(self, sight_radius):
        super(SightRadius, self).__init__()
        self.sight_radius = sight_radius


class Faction(Leaf):
    """
    The faction attribute keeps track of the faction.

    All other factions are concidered hostile.
    """

    PLAYER = 0
    MONSTER = 1

    def __init__(self, faction):
        super(Faction, self).__init__()
        self.faction = faction


class GraphicChar(Leaf):
    """
    Composites holding this has a graphical representation as a char.
    """
    def __init__(self, symbol, color_bg, color_fg):
        super(GraphicChar, self).__init__()
        self.symbol = symbol
        self.color_bg = color_bg
        self.color_fg = color_fg
        self._status_cycle_colors = []
        self._blink_color_fg_queue = []

    def draw_no_effect(self, position):
        """
        Draws the char on the given position on the console.

        Bypasses all effects.
        """
        if(not self.color_bg is None):
            console.set_color_bg(position, self.color_bg)
        if(not self.color_fg is None):
            console.set_color_fg(position, self.color_fg)
        if(not self.symbol is None):
            console.set_symbol(position, self.symbol)

    def draw(self, position):
        """
        Draws the char on the given position on the console.
        """
        self.draw_no_effect(position)
        if(len(self._blink_color_fg_queue) > 0):
            console.set_color_fg(position, self._blink_color_fg_queue.pop())

    def draw_unseen(self, screen_position):
        """
        Draws the char as it looks like outside the field of view.
        """
        console.set_colors_and_symbol(screen_position,
                                      colors.UNSEEN_FG,
                                      colors.UNSEEN_BG, self.symbol)

    def set_fg_blink_colors(self, colors):
        """
        Sets the foreground blink queue.

        These colors will be drawn as an effect,
        the regular colors won't be drawn until the blink queue is empty.
        """
        self._blink_color_fg_queue = colors


class Description(Leaf):
    """
    Composites holding this has some describing text and a name.
    """
    def __init__(self, name="XXX_UNNAMED_XXX",
                 description="XXX_Description_XXX"):
        super(Description, self).__init__()
        self.name = name
        self.description = description


class Health(Leaf):
    """
    Health Component. Composites holding this has health points.

    Attributes:
        _health_counter (Counter): Holds the min, max and current health.
    """
    def __init__(self, max_hp):
        self._health_counter = counter.Counter(max_hp, max_hp)

    """
    Increases the health by an amount.
    """
    def Heal(self, heal_ammount):
        self._health_counter.increase(heal_ammount)

    """
    Decreases the health by an amount.
    """
    def Damage(self, damage_ammount):
        self._health_counter(damage_ammount)


class MemoryMap(Leaf):
    """
    A representation of the dungeon as seen by an entity.
    """
    def __init__(self, max_hp):
        super(MemmoryMap, self).__init__()
        self._memory_map = []

    def get_memory_of_map(self, dungeon_level):
        self.set_memory_map_if_not_set(dungeon_level)
        return self._memory_map[dungeon_level.depth]

    def set_memory_map_if_not_set(self, dungeon_level):
        """
        Lazily initiates unknown dungeon to the depth needed.
        """
        depth = dungeon_level.depth
        while(len(self._memory_map) <= depth):
            self._memory_map.append(None)
            if(self._memory_map[depth] is None):
                self._memory_map[depth] =\
                    dungeon_level.unknown_level_map(dungeon_level.width,
                                                    dungeon_level.height,
                                                    dungeon_level.depth)

    def update_memory_of_tile(self, tile, position, depth):
        """
        Writes the entity memory of a tile, to the memory map.
        """
        if (tile.get_first_entity() is self):
            return  # No need to remember where you was, you are not there.
        self.set_memory_map_if_not_set(self.dungeon_level)
        x, y = position
        self._memory_map[depth].tile_matrix[y][x] = tile.copy()


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


ITEM_CAPACITY = 16


class Inventory(Leaf):
    """
    Holds the Items an entity is carrying.
    """
    def __init__(self, entity):
        super(Inventory, self).__init__()
        self._items = []
        self._entity = entity
        self._item_capacity = ITEM_CAPACITY

    @property
    def items(self):
        return self._items

    def try_add(self, item):
        """
        Tries to add an item to the inventory.

        Returns True on success otherwise False.
        """
        if(not self.has_room_for_item()):
            return False
        else:
            item.try_remove_from_dungeon()
            self._items.append(item)
            item.inventory = self
            return True

    def has_room_for_item(self):
        """
        Returns true if the inventory has room for another item.
        """
        return len(self._items) + 1 <= self._item_capacity

    def can_drop_item(self, item):
        """
        Returns true if it is a legal action to drop the item.
        """
        return item.can_move(self._entity.position,
                             self._entity.dungeon_level)

    def try_drop_item(self, item):
        """
        Tries to drop an item to the ground.

        Returns True on success otherwise False.
        """
        drop_successful = item.try_move(self._entity.position,
                                        self._entity.dungeon_level)
        if drop_successful:
            self.remove_item(item)
        return drop_successful

    def remove_item(self, item):
        """
        Removes item from the inventory.
        """
        self._items.remove(item)
        item.inventory = None

    def has_item(self, item):
        """
        Returns true if the item instance is in the inventory, false otherwise.
        """
        return item in self._items

    def is_empty(self):
        """
        Returns true the inventory is empty, false otherwise.
        """
        return len(self._items) <= 0

    def items_of_equipment_type(self, type_):
        """
        Returns a list of all items in the inventory of the given type.
        """
        return [item for item in self._items if item.equipment_type == type_]
