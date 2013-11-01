from compositecore import Leaf


class Description(Leaf):
    """
    Composites holding this has some describing text and a name.
    """
    def __init__(self, name="XXX_UNNAMED_XXX",
                 description="XXX_Description_XXX"):
        super(Description, self).__init__()
        self.name = name
        self.description = description
        self.component_type = "description"

    def copy(self):
        """
        Makes a copy of this component.
        """
        return Description(self.name, self.description)


class EntityMessages(Leaf):
    """
    Holds the text messages that may be sent by the parent entity.
    """
    def __init__(self, random, death):
        super(EntityMessages, self).__init__()
        self.component_type = "entity_messages"
        self.random = random
        self.death = death
