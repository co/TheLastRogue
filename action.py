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


class PickUpItemAction(Action):
    def __init__(self):
        super(PickUpItemAction, self).__init__()
        self.component_type = "pick_up_item_action"
        self.name = "Pick Up"
        self.display_order = 70

    def can_act(self, **kwargs):
        item = self._get_item_on_floor()
        print "time to pickup", item
        return (not item is None and
                self.parent.inventory.has_room_for_item(item))

    def act(self, **kwargs):
        item = self._get_item_on_floor()
        pickup_succeded = self.parent.inventory.try_add(item)
        if(pickup_succeded):
            message = "Picked up: " + item.description.name
            messenger.message(message)
            self.parent.actor.newly_spent_energy += gametime.single_turn

    def _get_item_on_floor(self):
        dungeon_level = self.parent.dungeon_level.value
        position = self.parent.position.value
        return dungeon_level.get_tile(position).get_first_item()

    def print_player_error(self, **kwargs):
        item = self._get_item_on_floor()
        if(not item is None and
           not self.parent.inventory.has_room_for_item(item)):
            message = "Could not pick up: " + item.description.name +\
                ", the inventory is full."
            messenger.message(message)
