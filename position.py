from compositecore import Leaf


class Position(Leaf):
    """
    Composites holding this has a position in the dungeon.
    """
    def __init__(self):
        super(Position, self).__init__()
        self.component_type = "position"
        self.position = (-1, -1)
