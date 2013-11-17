import gametime
from messenger import messenger
from compositecore import Leaf


#  Arguments:
SOURCE_ENTITY = "source_entity"
TARGET_ENTITY = "target_entity"
GAME_STATE = "game_state"
EQUIPMENT_SLOT = "equipment_slot"
ACTION = "action"


class Action(Leaf):
    """
    Abstract component, all sub components of this type should defina an
    action. A entity should be able to use the parent entity
    using the action.
    """
    def __init__(self):
        super(Action, self).__init__()
        self.tags.add("user_action")
        self.name = "XXX_Action_Name_XX"
        self.display_order = 100
        self.energy_cost = gametime.single_turn

    def __call__(self, *args, **kwargs):
        self.act(*args, **kwargs)

    def delayed_call(self, *args, **kwargs):
        return DelayedFunctionCall(self, *args, **kwargs)

    def act(self, **kwargs):
        """
        The action that this component defines.
        """
        pass

    def can_act(self, **kwargs):
        """
        Returns true if it is valid to call the act method.
        """
        return True

    def add_energy_spent_to_entity(self, entity):
        """
        Help method for spending energy for the act performing entity.
        """
        entity.actor.newly_spent_energy += self.energy_cost


class DelayedFunctionCall(object):
    def __init__(self, function, **kwargs):
        self.function = function
        self.kwargs = kwargs

    def __call__(self):
        self.function(**self.kwargs)