import action
import entityeffect


class UnequipAction(action.Action):
    """
    An Item with this component can be unequipped.

    If an item is already in that
    equipment slot that item will be unequipped first.
    """
    def __init__(self):
        super(UnequipAction, self).__init__()
        self.component_type = "unequip_action"
        self.name = "Remove"
        self.display_order = 90

    def act(self, **kwargs):
        """
        Will attempt to unequip item to the given equipment_slot.
        """
        target_entity = kwargs[action.TARGET_ENTITY]
        source_entity = kwargs[action.SOURCE_ENTITY]
        equipment_slot = kwargs[action.EQUIPMENT_SLOT]
        if(target_entity.equipment.slot_is_equiped(equipment_slot)):
            self._unequip(target_entity, equipment_slot)
            self.add_energy_spent_to_entity(source_entity)

    def can_act(self, **kwargs):
        """
        Returns true if it's legal for the entity to unequip item.
        """
        source_entity = kwargs[action.SOURCE_ENTITY]
        equipment_slot = kwargs[action.EQUIPMENT_SLOT]
        return (source_entity.inventory.has_room_for_item() and
                source_entity.equipment.slot_is_equiped(equipment_slot))

    def _unequip(self, target_entity, equipment_slot):
        """
        Performs the actual unequip.
        """
        if(not target_entity.equipment.slot_is_equiped(equipment_slot)):
            return
        unequip_effect = entityeffect.Unequip(target_entity, equipment_slot)
        target_entity.effect_queue.add(unequip_effect)
