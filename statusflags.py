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
        self.component_type = "status_flags"
        self._status_flags = set()
        self._temp_status_flags = set()

    def has_status(self, status):
        """
        Returns True if parent entity has the status given.
        """
        next = self.next
        if(not next is None):
            return (status in self._status_flags or
                    status in self._temp_status_flags or
                    next.has_status(status))
        else:
            return (status in self._status_flags or
                    status in self._temp_status_flags)

    def add_temp_status(self, status):
        """
        Adds a temporary status that will be removed the next tick.
        """
        self._temp_status_flags.add(status)

    def before_tick(self, time):
        self._temp_status_flags = set()
