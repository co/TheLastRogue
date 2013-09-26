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
        self._parent = None
        pass

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value
        self.on_parent_changed()

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

    def message(self, message):
        """
        A method hook for broadcasting a message down the component tree.
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
        self.children = []

    def add_child(self, child):
        """
        Adds a child component to this component.
        If the child already has a parent an exception is thrown.
        """
        self.children.append(child)
        if(not child.parent is None):
            print "Component {0} tried ta add_child"\
                "component: {1} to its children."\
                "But it already"\
                "had parent: {2}.".format(str(self),
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

    def message(self, message):
        """
        Sends message to all child components.
        """
        map(lambda x: x.message(message), self.children)

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
