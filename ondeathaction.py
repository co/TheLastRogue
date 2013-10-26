from compositecore import Leaf
from statusflags import StatusFlags
import spawner
from messenger import messenger, Message


class OnDeathAction(Leaf):
    """
    The action will be called when parent Entity dies.
    """
    def __init__(self):
        super(OnDeathAction, self).__init__()
        self.component_type = "on_death_action"

    def act(self):
        pass

    def can_act(self):
        return True


class EntityDeathAction(OnDeathAction):
    """
    The action will be called when parent Entity dies.
    """
    def __init__(self):
        super(EntityDeathAction, self).__init__()

    def act(self):
        if(self.parent.status_flags.has_status(StatusFlags.LEAVES_CORPSE)):
            spawner.spawn_corpse_of_entity(self.parent)
        self.parent.dungeon_level.value.remove_actor_if_present(self.parent)
        self.parent.mover.try_remove_from_dungeon()
        messenger.message(Message(self.parent.entity_messages.death))
