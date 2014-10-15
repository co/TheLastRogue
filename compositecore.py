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

    @property
    def parent(self):
        if self._parent is None:
            raise LookupError("Tried to get parent of {0}, "
                              "but parent was not set".format(str(self)))
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value
        if not value is None:
            self.on_parent_changed()

    def has_parent(self):
        return not self._parent is None

    @property
    def next(self):
        """
        Gets the next sibling of the same type,
        allows components to decorate components of the same type.
        """
        if not self.has_parent():
            return None
        if self.parent.get_original_child(self.component_type) is self:
            return None
        siblings = \
            self.parent.get_spoofed_children_of_type(self.component_type)
        next_index = siblings.index(self) + 1
        if len(siblings) > next_index:
            return siblings[next_index]
        return self.parent.get_original_child(self.component_type)

    def on_parent_changed(self):
        """
        A method hook called when the parent changes.
        """
        pass

    def update(self, *args, **kw):
        """
        A method hook for updating the component tree.
        """
        pass

    def first_tick(self, time):
        """
        A method hook for updating the component tree before tick.
        """
        pass

    def before_tick(self, time):
        """
        A method hook for updating the component tree before tick.
        """
        pass

    def on_tick(self, time):
        """
        A method hook for updating the component tree on tick.
        """
        pass

    def after_tick(self, time):
        """
        A method hook for updating the component tree after tick.
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
        if self._parent is None:
            raise Exception("ERROR: Tries to find sibling {0} "
                            "of component {1} but it "
                            "has no parent!".format(str(component_type),
                                                    str(self)))
        return self.parent.has(component_type)


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
        self._spoofed_children = {}
        self._children = {}
        self._children_tag_table = {}

    def __getinitargs__(self):
        return ()

    def get_child(self, component_type):
        return self.__getattr__(component_type)

    def set_child(self, child):
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
        if not child._parent is None:
            raise Exception("Component {0} tried ta add_child"
                            "component: {1} to its children."
                            "But it already"
                            "had parent: {2}.".format(str(self), str(child), str(child.parent)))
        if self.has(child.component_type):
            self.remove_component_of_type(child.component_type)
        self._children[child.component_type] = child
        self._add_child_to_tag_table(child)
        child.parent = self

    def add_spoof_child(self, child):
        """
        Adds a spoofed child component to this composite.
        If the child already has a parent an exception is thrown.
        """
        if child.tags is None:
            raise Exception("Component {0} tried to add_child "
                            "component: {1} to its children. "
                            "But tags "
                            "was not set.".format(str(self), str(child)))
        if child.component_type is None:
            raise Exception("Component {0} tried to add_child "
                            "component: {1} to its children. "
                            "But component_type "
                            "was not set.".format(str(self), str(child)))
        if not child._parent is None and child.parent != self:
            raise Exception("Component {0} tried to add_child "
                            "component: {1} to its children. "
                            "But it already "
                            "had parent: {2}.".format(str(self), str(child), str(child.parent)))
        if not child.component_type in self._spoofed_children:
            self._spoofed_children[child.component_type] = []
        self._spoofed_children[child.component_type].append(child)
        self._add_child_to_tag_table(child)
        child.parent = self

    def _add_child_to_tag_table(self, child):
        for tag in child.tags:
            if not tag in self._children_tag_table:
                self._children_tag_table[tag] = []
            self._children_tag_table[tag].append(child)

    def _remove_child_from_tag_table(self, child):
        for tag in child.tags:
            if tag in self._children_tag_table:
                self._children_tag_table[tag].remove(child)

    def reset_spoofed_children(self):
        """
        Removes all spoofed children.
        """
        for child_type in self._spoofed_children.values():
            for child in child_type:
                self.remove_component(child)
        self._spoofed_children = {}  # Unecessary?

    def remove_component(self, child):
        """
        Removes a child component from this component.
        """
        if (child.component_type in self._children and
                    child is self._children[child.component_type]):
                child.parent = None
                del self._children[child.component_type]
        if (child.component_type in self._spoofed_children and
                    child in self._spoofed_children[child.component_type]):
            self._spoofed_children[child.component_type].remove(child)
            child.parent = None
        self._remove_child_from_tag_table(child)
        return child

    def remove_component_of_type(self, component_type):
        """
        Removes a child component of a type of this component.
        """
        return self.remove_component(self._children[component_type])

    def update(self):
        """
        Runs update on all child components.
        """
        map(lambda x: x.update(), self._children.values())

    def first_tick(self, time):
        """
        Runs first_tick on all child components.
        """
        visited_component_types = set()
        for component_type, component in self._spoofed_children.iteritems():
            visited_component_types.add(component_type)
            component[0].first_tick(time)
        components_without_spoof = [component for key, component in self._children.iteritems()
                                    if not key in visited_component_types]
        for component in components_without_spoof:
            component.first_tick(time)

    def before_tick(self, time):
        """
        Runs before_tick on all child components.
        """
        visited_component_types = set()
        for component_type, component in self._spoofed_children.iteritems():
            visited_component_types.add(component_type)
            component[0].before_tick(time)
        components_without_spoof = [component for key, component in self._children.iteritems()
                                    if not key in visited_component_types]
        for component in components_without_spoof:
            component.before_tick(time)

    def on_tick(self, time):
        """
        Runs on_tick on all child components.
        """
        visited_component_types = set()
        for component_type, component in self._spoofed_children.iteritems():
            visited_component_types.add(component_type)
            component[0].on_tick(time)
        components_without_spoof = [component for key, component in self._children.iteritems()
                                    if not key in visited_component_types]
        for component in components_without_spoof:
            component.on_tick(time)

    def after_tick(self, time):
        """
        Runs after_tick on all child components.

        It also resets all spoofed children.
        """
        visited_component_types = set()
        for component_type, component in self._spoofed_children.iteritems():
            visited_component_types.add(component_type)
            component[0].after_tick(time)
        components_without_spoof = [component for key, component in self._children.iteritems()
                                    if not key in visited_component_types]
        for component in components_without_spoof:
            component.after_tick(time)

    def message(self, message):
        """
        Sends message to all child components.
        """
        map(lambda x: x.message(message), self._children.values())

    def __getattr__(self, component_type):
        if component_type == "_spoofed_children" or component_type == "_children":
            raise AttributeError("Tried to access field {0} from composite {1} "
                                 "But it doesn't exist.".format(str(component_type),
                                                                str(self)))
        try:
            if (component_type in self._spoofed_children and
                        len(self._spoofed_children[component_type]) > 0):
                return self._spoofed_children[component_type][0]
            return self._children[component_type]
        except KeyError:
            raise AttributeError("Tried to access component {0} from composite {1} "
                                 "But it doesn't exist.".format(str(component_type), str(self)))

    def get_original_child(self, component_type):
        """
        Gets the "real" child of the composite.
        """
        return self._children[component_type]

    def get_spoofed_children_of_type(self, component_type):
        try:
            return self._spoofed_children[component_type]
        except KeyError:
            raise Exception("Tried to access components of type"
                            " {0} from composite {1} "
                            "But it doesn't exist.".format(str(component_type),
                                                           str(self)))

    def has(self, component_type):
        """
        Returns true if this component has a child of the given type.

        False otherwise.
        """
        return component_type in self._children

    def has_tag(self, tag):
        """
        Returns true if this component has the given tag.

        False otherwise.
        """
        return tag in self.tags

    def get_children_with_tag(self, tag):
        """
        Gets the list of all children with the given tag.
        """
        if not tag in self._children_tag_table:
            return []
        return self._children_tag_table[tag]


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
