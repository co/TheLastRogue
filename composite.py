import counter
import entity
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

    def update(self):
        """
        A method hook for updating the component tree.
        """
        pass


class Leaf(Component):
    """
    Abstract leaf class of composite design pattern.

    Component classes of leaf type should inherit from this class.
    """
    def __init__(self, *args, **kw):
        super(Leaf, self).__init__(*args, **kw)
        pass


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

    def remove_child(self, child):
        """
        Removes a child component to this component.
        """
        self.children.remove(child)
        child.parent = None

    def update(self):
        """
        Runs update on all child components.
        """
        map(lambda x: x.update(), self.children)

    def get_child(self, component_type):
        """
        Gets the first child which is of the given type.
        """
        return next(child for child in self.children
                    if isinstance(child, component_type))


class Player(Composite):
    """
    A composite component representing the player character.
    """
    def __init__(self):
        super(Player, self).__init__()
        self.add_child(DungeonPosition())
        self.add_child(Description())
        self.add_child(GraphicChar(symbol.GUNSLINGER_THIN,
                                   None, colors.WHITE))

        self.add_child(Health(10))
        self.add_child(EntityStats(3, entity.Faction.Player))
### Speed
### Equipment
### Inventory
### EffectQueue
### StatusFlags
### GameState???
### GamePiece
### DungeonMap


class DungeonPosition(Leaf):
    """
    Composites holding this has a position in the dungeon.
    """
    def __init__(self):
        super(DungeonPosition, self).__init__()
        self.position = (-1, -1)
        self.depth = -1
        self.dungeon_level = None


class MemmoryMap(Leaf):
    """
    Composites holding this has a position in the dungeon.
    """
    def __init__(self):
        super(DungeonPosition, self).__init__()
        self.position = (-1, -1)
        self.depth = -1


class EntityStats(Leaf):
    """
    Composites holding this has a position in the dungeon.
    """
    def __init__(self, strength, faction, sight_radius):
        super(EntityStats, self).__init__()
        self.strength = strength
        self.faction = faction
        self.sight_radius = sight_radius


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
        health_counter (Counter): Holds the min, max and current health.
    """
    def __init__(self, max_hp):
        self.health_counter = counter.Counter(max_hp, max_hp)

    """
    Increases the health by an amount.
    """
    def Heal(self, heal_ammount):
        self.health_counter.increase(heal_ammount)

    """
    Decreases the health by an amount.
    """
    def Damage(self, damage_ammount):
        self.health_counter(damage_ammount)
