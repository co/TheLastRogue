from compositecore import Leaf
import spawner
from messenger import msg


class RemoveEntityOnDeath(Leaf):
    """
    Will remove the parent from the dungeon when parent Entity dies.
    """
    def __init__(self):
        super(RemoveEntityOnDeath, self).__init__()
        self.component_type = "remove_on_death"

    def after_tick(self, time):
        if self.parent.health.is_dead():
            self.parent.dungeon_level.value
            self.parent.mover.try_remove_from_dungeon()


class PrintDeathMessageOnDeath(Leaf):
    """
    Will print death message when parent Entity dies.
    """
    def __init__(self):
        super(PrintDeathMessageOnDeath, self).__init__()
        self.component_type = "print_death_message_on_death"

    def on_tick(self, time):
        if self.parent.health.is_dead():
            msg.message(self.parent.entity_messages.death)


class LeaveCorpseOnDeath(Leaf):
    """
    Will remove the parent from the dungeon when parent Entity dies.
    """
    def __init__(self):
        super(LeaveCorpseOnDeath, self).__init__()
        self.component_type = "leave_corpse_on_death"

    def on_tick(self, time):
        if self.parent.health.is_dead():
            spawner.spawn_corpse_of_entity(self.parent)
