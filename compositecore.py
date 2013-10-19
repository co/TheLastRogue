from itertools import chain


class Component(object):
    """
    Abstract base class of composite design pattern.

    New classes should not inherit from this class but from
    the Leaf or Composite classes instead.

    Attributes:
        parent (Component): The parent component.
        Is None if this is a root component.
        component_type (string): The component_type, a composite can only
        have one active child of a given component_type.
        tags (Set of strings): Tags can be used as a second
        means of identifying a component.
    """
    def __init__(self, *args, **kw):
        self._parent = None
        self.component_type = None
        self.tags = set()
        self.to_be_removed = False
        pass

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value
        self.on_parent_changed()

    @property
    def next(self):
        """
        Gets the next sibling of the same type,
        allows components to decorate components of the same type.
        """
        siblings = self.parent.get_children_of_type(self.component_type)
        next_index = siblings.index(self) + 1
        if(len(siblings) > next_index):
            return siblings[next_index]
        return None

    def on_parent_changed(self):
        """
        A method hook called when the parent changes.
        """
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

    def on_tick(self, time):
        """
        A method hook for updating the component tree on tick.
        """
        pass

    def message(self, message):
        """
        A method hook for broadcasting a message down the component tree.
        """
        pass

    def has_sibling(self, component_type):
        """
        Returns true if this components parent has a child of the given type.

        False otherwise.
        """
        if(self.parent is None):
            print "ERROR: Tries to find sibling {0} "\
                "of component {1} but it "\
                "has no parent!".format(str(component_type), str(self))
            raise
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
        self._children = {}

    def add_child(self, child):
        """
        Adds a child component to this component.
        If the child already has a parent an exception is thrown.
        """
        if child.tags is None:
            raise Exception("Component {0} tried ta add_child"
                            "component: {1} to its children."
                            "But tags"
                            "was not set.".format(str(self), str(child)))
        if child.component_type is None:
            raise Exception("Component {0} tried ta add_child"
                            "component: {1} to its children."
                            "But component_type"
                            "was not set.".format(str(self), str(child)))
        if(not child.parent is None):
            raise Exception("Component {0} tried ta add_child"
                            "component: {1} to its children."
                            "But it already"
                            "had parent: {2}.".format(str(self),
                                                      str(child),
                                                      str(child.parent)))
        if not child.component_type in self._children:
            self._children[child.component_type] = []
        self._children[child.component_type].append(child)
        child.parent = self

    def remove_component(self, component):
        """
        Removes a child component to this component.
        """
        return self._children[component.component_type].remove(component)

    def remove_components_flagged_for_removal(self):
        """
        Removes a child component to this component.
        """
        for component_list in self._children.values:
            to_be_removed = [component for component in component_list
                             if component.to_be_removed]
            for component in to_be_removed:
                component_list.remove(component)

    def update(self):
        """
        Runs update on all child components.
        """
        map(lambda x: x.update(),
            chain.from_iterable(self._children.values()))

    def on_tick(self, time):
        """
        Runs on_tick on all child components.
        """
        map(lambda x: x.on_tick(time),
            chain.from_iterable(self._children.values()))

    def message(self, message):
        """
        Sends message to all child components.
        """
        map(lambda x: x.message(message),
            chain.from_iterable(self._children.values()))

    def __getattr__(self, component_type):
        if(not isinstance(component_type, basestring)):
            raise Exception("ERROR: component_type should be string")
        if(not component_type in self._children or
           len(self._children[component_type]) < 1):
            raise Exception("Tried to access component {0} from composite {1} "
                            "But it doesn't exist.".format(str(component_type),
                                                           str(self)))
        return self._children[component_type][0]

    def get_children_of_type(self, component_type):
        if(not isinstance(component_type, basestring)):
            raise Exception("ERROR: component_type should be string")
        if(not component_type in self._children or
           len(self._children[component_type]) < 1):
            raise Exception("Tried to access components of type"
                            " {0} from composite {1} "
                            "But it doesn't exist.".format(str(component_type),
                                                           str(self)))
        return self._children[component_type]

    def has_child(self, component_type):
        """
        Returns true if this component has a child of the given type.

        False otherwise.
        """
        return (component_type in self._children and
                len(self._children[component_type]) > 0)

    def get_children_with_tag(self, tag):
        """
        Gets the list of all children with the given tag.
        """
        return [child[0] for child in self._children.values()
                if tag in child[0].tags]


class CompositeMessage(object):
    """
    Enumerator defining class. Defines all messages that may be sent.
    """
    DUNGEON_LEVEL_CHANGED = 0
    POSITION_CHANGED = 1

    def __init__(self):
        """
        Should not be initiated.
        """
        raise
