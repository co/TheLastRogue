from compositecore import Leaf


class Description(Leaf):
    """
    Composites holding this has some describing text and a name.
    """
    def __init__(self, name, description):
        super(Description, self).__init__()
        self.component_type = "description"
        self._name = name
        self.description = description

    @property
    def name(self):
        return self._name

    @property
    def long_name(self):
        if self.parent.has_child("is_named"):
            return self._name
        else:
            return "the " + self._name
    @name.setter
    def name(self, value):
        self._name = value

    def copy(self):
        """
        Makes a copy of this component.
        """
        return Description(self.name, self.description)


class EntityMessages(Leaf):
    """
    Holds the text messages that may be sent by the parent entity.
    """
    def __init__(self, notice, death):
        super(EntityMessages, self).__init__()
        self.component_type = "entity_messages"
        self.notice = notice
        self.death = death