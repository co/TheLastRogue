import counter
import terrain
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
        self.add_child(Faction(Faction.Player))
        self.add_child(SightRadius(6))
        self.add_child(StatusFlags(6))
        #self.add_child(inventory.Inventory(6))
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


class Mover(Leaf):
    """
    Component for moving and checking if a move is legal.
    """

    def can_move(self, new_position, new_dungeon_level=None):
        """
        Checks if parent comoponent can move to new position.
        """
        if(new_dungeon_level is None):
            new_dungeon_level =\
                self.get_sibling_of_type(DungeonLevel).dungeon_level
        if(not new_dungeon_level.has_tile(new_position)):
            return False
        new_tile = new_dungeon_level.get_tile(new_position)
        return (self._can_fit_on_tile(new_tile) and
                self._can_pass_terrain(new_tile.get_terrain()))

    def try_move(self, new_position, new_dungeon_level=None):
        """
        Tries to move parent to new position.

        Returns true if it is successful, false otherwise.
        """
        if(new_dungeon_level is None):
            new_dungeon_level =\
                self.get_sibling_of_type(DungeonLevel).dungeon_level
        if(self.can_move(new_position, new_dungeon_level)):
            self._move(new_position, new_dungeon_level)
            return True
        return False

    def _move(self, new_position, dungeon_level):
        """
        Moves parent to new position, assumes that it fits there.
        """
        self.try_remove_from_dungeon()
        new_tile = dungeon_level.get_tile(new_position)
        piece_type = self.get_sibling_of_type(GamePieceType).value
        new_tile.game_pieces[piece_type].append(self.parent)
        print new_tile.game_pieces
        self.get_sibling_of_type(Position).position = new_position
        dungeon_level_module = DungeonLevel()
        dungeon_level_module.dungeon_level = dungeon_level
        self.parent.add_child(dungeon_level_module)

    def replace_move(self, new_position, new_dungeon_level=None):
        """
        Moves parent to new position and replaces what was already there.
        """
        if(new_dungeon_level is None):
            new_dungeon_level =\
                self.get_sibling_of_type(DungeonLevel).dungeon_level
        if(not new_dungeon_level.has_tile(new_position)):
            return False
        new_tile = new_dungeon_level.get_tile(new_position)
        self.try_remove_from_dungeon()
        piece_type = self.get_sibling_of_type(GamePieceType).value
        new_place = new_tile.game_pieces[piece_type]
        for piece in new_place:
            piece.get_child_of_type(Mover).try_remove_from_dungeon()
        self.try_move(new_position, new_dungeon_level)

    def _can_fit_on_tile(self, tile):
        """
        Checks if the parent can fit on the tile.
        """
        piece_type = self.get_sibling_of_type(GamePieceType)
        return (len(tile.game_pieces[piece_type.value]) <
                piece_type.max_instances_in_tile)

    def _can_pass_terrain(self, terrain_to_pass):
        """
        Checks if the parent can move through a terrain.
        """
        if(terrain_to_pass is None):
            return False
        if(not terrain_to_pass.is_solid()):
            return True
        status_flags = self.get_sibling_of_type(StatusFlags)
        if(not status_flags is None and
           status_flags.has_status(StatusFlags.CAN_OPEN_DOORS) and
           isinstance(terrain_to_pass, terrain.Door)):
            return True
        return False

    def try_remove_from_dungeon(self):
        """
        Tries to remove parent from dungeon.
        """
        if(not self.has_sibling(DungeonLevel)):
            return True
        position = self.get_sibling_of_type(Position).position
        tile_i_might_be_on = (self.get_sibling_of_type(DungeonLevel).
                              dungeon_level.get_tile(position))

        piece_type = self.get_sibling_of_type(GamePieceType).value
        pieces_i_might_be_among = \
            tile_i_might_be_on.game_pieces[piece_type]
        if self.has_sibling(DungeonLevel):
            self.parent.remove_child_of_type(DungeonLevel)
        if(any(self.parent is piece for piece in pieces_i_might_be_among)):
            pieces_i_might_be_among.remove(self.parent)
            return True
        return False


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
        self.dungeon_level = None


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
