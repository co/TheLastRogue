from compositecore import Leaf


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
