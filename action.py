import gametime
from messenger import messenger
from compositecore import Leaf


#  Arguments:
SOURCE_ENTITY = "source_entity"
TARGET_ENTITY = "target_entity"
GAME_STATE = "game_state"
EQUIPMENT_SLOT = "equipment_slot"
ACTION = "action"


#class Action(Leaf):
#    def __init__(self):
#        self.name = "XXX_Action_Name_XX"
#        self.display_order = 100
#        self.energy_cost = gametime.single_turn
#
#    def act(self, **kwargs):
#        pass
#
#    def can_act(self, **kwargs):
#        return True
#
#    def add_energy_spent_to_entity(self, entity):
#        entity.newly_spent_energy += self.energy_cost
#
#    def copy(self):
#        result = self.__class__()
#        return result
#
#
#class ItemAction(Action):
#    def __init__(self, source_item):
#        super(ItemAction, self).__init__()
#        self.name = "XXX_Item_Action_Name_XXX"
#        self.source_item = source_item
#
#    def remove_from_inventory(self):
#        self.source_item.inventory.remove_item(self.source_item)
#
#    def copy(self):
#        result = self.__class__(self.source_item)
#        return result

#
## Unused?
#class EquipAction(ItemAction):
#    def __init__(self, source_item):
#        super(EquipAction, self).__init__(source_item)
#        self.name = "Equip"
#        self.display_order = 90
#
#    def act(self, **kwargs):
#        target_entity = kwargs[TARGET_ENTITY]
#        source_entity = kwargs[SOURCE_ENTITY]
#        self.equip(target_entity)
#        self.add_energy_spent_to_entity(source_entity)
#
#    def can_act(self, **kwargs):
#        target_entity = kwargs[TARGET_ENTITY]
#        return target_entity.equipment.can_equip(self.source_item)
#
#    def equip(self, target_entity):
#        equip_effect = entityeffect.Equip(target_entity,
#                                          target_entity, self.source_item)
#        target_entity.add_entity_effect(equip_effect)
#
#
#class UnEquipAction(ItemAction):
#    def __init__(self, source_item):
#        super(UnEquipAction, self).__init__(source_item)
#        self.name = "UnEquip"
#        self.display_order = 90
#
#    def act(self, **kwargs):
#        target_entity = kwargs[TARGET_ENTITY]
#        source_entity = kwargs[SOURCE_ENTITY]
#        equipment_slot = kwargs[EQUIPMENT_SLOT]
#        if(not self.source_item is None):
#            self.unequip(target_entity, equipment_slot)
#            self.add_energy_spent_to_entity(source_entity)
#
#    def can_act(self, **kwargs):
#        source_entity = kwargs[SOURCE_ENTITY]
#        equipment_slot = kwargs[EQUIPMENT_SLOT]
#        return (source_entity.inventory.has_room_for_item() and
#                source_entity.equipment.slot_is_equiped(equipment_slot))
#
#    def unequip(self, target_entity, equipment_slot):
#        if(not target_entity.equipment.slot_is_equiped(equipment_slot)):
#            return
#        unequip_effect = entityeffect.UnEquip(target_entity,
#                                              target_entity, equipment_slot)
#        target_entity.add_entity_effect(unequip_effect)
#
#
#class ReEquipAction(EquipAction):
#    def __init__(self, source_item):
#        super(ReEquipAction, self).__init__(source_item)
#        self.name = "Equip"
#        self.display_order = 90
#
#    def act(self, **kwargs):
#        source_entity = kwargs[SOURCE_ENTITY]
#        if(EQUIPMENT_SLOT in kwargs):
#            equipment_slot = kwargs[EQUIPMENT_SLOT]
#        else:
#            equipment_slot = self.get_equipment_slot(source_entity)
#        old_item = None
#        if(source_entity.equipment.slot_is_equiped(equipment_slot)):
#            old_item = source_entity.equipment.unequip(equipment_slot)
#        self.re_equip(source_entity, equipment_slot)
#        if(not old_item is None):
#            source_entity.inventory.try_add(old_item)
#        self.add_energy_spent_to_entity(source_entity)
#
#    def get_equipment_slot(self, source_entity):
#        open_slots = (source_entity.equipment.get_open_slots_of_type
#                      (self.source_item.equipment_type))
#        if(len(open_slots) > 0):
#            return open_slots[0]
#        else:
#            return (source_entity.equipment.get_slots_of_type
#                    (self.source_item.equipment_type))[0]
#
#    def can_act(self, **kwargs):
#        return True
#
#    def re_equip(self, target_entity, equipment_slot):
#        re_equip_effect = entityeffect.ReEquip(target_entity,
#                                               target_entity,
#                                               equipment_slot,
#                                               self.source_item)
#        target_entity.add_entity_effect(re_equip_effect)
#        target_entity.inventory.remove_item(self.source_item)
#
#
#class DrinkAction(ItemAction):
#    def __init__(self, source_item):
#        super(DrinkAction, self).__init__(source_item)
#        self.name = "Drink"
#        self.display_order = 90
#
#    def act(self, **kwargs):
#        target_entity = kwargs[TARGET_ENTITY]
#        source_entity = kwargs[SOURCE_ENTITY]
#        self.drink(target_entity)
#        self.remove_from_inventory()
#        self.add_energy_spent_to_entity(source_entity)
#
#    def drink(self):
#        pass
#
#
#class HealingPotionDrink(DrinkAction):
#    def __init__(self, source_item):
#        super(HealingPotionDrink, self).__init__(source_item)
#        self.min_health = 5
#        self.max_health = 10
#
#    def drink(self, target_entity):
#        health = random.randrange(self.min_health, self.max_health)
#        heal_effect = entityeffect.Heal(target_entity, target_entity, health)
#        target_entity.add_entity_effect(heal_effect)

#
#class DropAction(ItemAction):
#    def __init__(self, source_item):
#        super(DropAction, self).__init__(source_item)
#        self.name = "Drop"
#        self.display_order = 110
#
#    def act(self, **kwargs):
#        source_entity = kwargs[SOURCE_ENTITY]
#        if(not self.source_item.inventory is None):
#            drop_successful =\
#                self.source_item.inventory.try_drop_item(self.source_item)
#            if(drop_successful):
#                self.add_energy_spent_to_entity(source_entity)
#        return
#

#class DescendStairsAction(Action):
#    def __init__(self):
#        super(DescendStairsAction, self).__init__()
#        self.name = "Descend Stairs"
#        self.display_order = 50
#
#    def act(self, **kwargs):
#        target_entity = kwargs[TARGET_ENTITY]
#        source_entity = kwargs[SOURCE_ENTITY]
#        current_dungeon_level = target_entity.dungeon_level
#        next_dungeon_level = current_dungeon_level.\
#            dungeon.get_dungeon_level(current_dungeon_level.depth + 1)
#        if(next_dungeon_level is None):
#            return False
#        destination_position = next_dungeon_level.up_stairs[0].position
#        target_entity.try_move(destination_position, next_dungeon_level)
#        self.add_energy_spent_to_entity(source_entity)
#
#

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

    def copy(self):
        """
        Copy function.
        """
        result = self.__class__()
        return result


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
        return (not item is None and
                self.parent.inventory.has_room_for_item())

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
        if(item is None and
           not self.parent.inventory.has_room_for_item()):
            message = "Could not pick up: " + item.description.name +\
                ", the inventory is full."
            messenger.message(message)
