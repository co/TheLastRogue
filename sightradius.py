from compositecore import Leaf


class SightRadius(Leaf):
    """
    Composites holding this has the sight_radius attribute.
    """
    def __init__(self, sight_radius):
        super(SightRadius, self).__init__()
        self.component_type = "sight_radius"
        self.sight_radius = sight_radius
