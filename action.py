import gametime
from compositecore import Leaf


#  Arguments:
SOURCE_ENTITY = "source_entity"
TARGET_ENTITY = "target_entity"
GAME_STATE = "game_state"
TARGET_POSITION = "target_position"
EQUIPMENT_SLOT = "equipment_slot"
ACTION = "action"
DESTINATION = "destination" #TODO: Replace with target_position?


class Action(Leaf):
    """
    Abstract component, all sub components of this type should define an
    action. A entity should be able to use the parent entity
    using the action.
    """
    def __init__(self, name="XXX_Action_Name_XXX", display_order=100, energy_cost=gametime.single_turn):
        super(Action, self).__init__()
        self.tags.add("user_action")
        self.name = name
        self.display_order = display_order
        self.energy_cost = energy_cost

    def __call__(self, *args, **kwargs):
        self.act(*args, **kwargs)

    def delayed_act(self, *args, **kwargs):
        return DelayedFunctionCall(self.act, *args, **kwargs)

    def delayed_can_act(self, *args, **kwargs):
        return DelayedFunctionCall(self.can_act, *args, **kwargs)

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


class TriggerAction(Action):
    """
    An action which also triggers like a trigger.
    """
    def __init__(self, name, display_order, tags=[], energy_cost=gametime.single_turn):
        super(TriggerAction, self).__init__(name=name, display_order=display_order, energy_cost=energy_cost)
        self.component_type = "trigger"
        self.tags.add("user_action")
        self.tags |= set(tags)
        self.name = name
        self.display_order = display_order
        self._energy_cost = gametime.single_turn

    def trigger(self, **kwargs):
        for c in self.parent.get_children_with_tag("triggered_effect"):
            if c.can_trigger(**kwargs):
                c.trigger(**kwargs)

    def can_trigger(self, **kwargs):
        return all(c.can_trigger(**kwargs) for c in self.parent.get_children_with_tag("triggered_effect"))

    def act(self, **kwargs):
        return self.trigger(**kwargs)

    def can_act(self, **kwargs):
        return self.can_trigger(**kwargs)


class DelayedFunctionCall(object):
    def __init__(self, function, **kwargs):
        self.function = function
        self.kwargs = kwargs

    def __call__(self):
        return self.function(**self.kwargs)
