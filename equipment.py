class EquipmentSlots(object):
    #  Armor
    HEADGEAR = 0
    ARMOR = 1
    GLOVES = 2
    BOOTS = 3

    #  Jewelry
    RIGHT_RING = 4
    LEFT_RING = 5
    AMULET = 6

    #  Weapons
    MELEE_WEAPON = 7
    RANGED_WEAPON = 8

    ALL = [HEADGEAR, ARMOR, GLOVES, BOOTS, RIGHT_RING,
           LEFT_RING, AMULET, MELEE_WEAPON, RANGED_WEAPON]


class EquipmentTypes(object):
    #  Armor
    HEADGEAR = 0
    ARMOR = 1
    GLOVES = 2
    BOOTS = 3

    #  Jewelry
    RING = 4
    AMULET = 5

    #  Weapons
    MELEE_WEAPON = 6
    RANGED_WEAPON = 7

    ALL = [HEADGEAR, ARMOR, GLOVES, BOOTS,
           RING, AMULET, MELEE_WEAPON, RANGED_WEAPON]


EquipmentTypeAllowedInSlot = {
    EquipmentSlots.HEADGEAR: EquipmentTypes.HEADGEAR,
    EquipmentSlots.ARMOR: EquipmentTypes.ARMOR,
    EquipmentSlots.GLOVES: EquipmentTypes.GLOVES,
    EquipmentSlots.BOOTS: EquipmentTypes.BOOTS,

    #  Jewelry
    EquipmentSlots.RIGHT_RING: EquipmentTypes.RING,
    EquipmentSlots.LEFT_RING: EquipmentTypes.RING,
    EquipmentSlots.AMULET: EquipmentTypes.AMULET,

    #  Weapons
    EquipmentSlots.MELEE_WEAPON: EquipmentTypes.MELEE_WEAPON,
    EquipmentSlots.RANGED_WEAPON: EquipmentTypes.RANGED_WEAPON
}


class Equipment(object):
    def __init__(self, entity):
        self._equipment = {
            EquipmentSlots.HEADGEAR: None,
            EquipmentSlots.ARMOR: None,
            EquipmentSlots.GLOVES: None,
            EquipmentSlots.BOOTS: None,

            EquipmentSlots.RIGHT_RING: None,
            EquipmentSlots.LEFT_RING: None,
            EquipmentSlots.AMULET: None,

            EquipmentSlots.MELEE_WEAPON: None,
            EquipmentSlots.RANGED_WEAPON: None
        }
        self.entity = entity

    def get(self, equipment_slot):
        return self._equipment[equipment_slot]

    def has_type(self, equipment_type):
        return (not self._equipment[EquipmentTypeAllowedInSlot[equipment_type]]
                is None)

    def slot_is_equiped(self, equipment_slot):
        return not self._equipment[equipment_slot] is None

    def unequip(self, equipment_slot):
        equipment = self._equipment[equipment_slot]
        equipment.unequip_effect(self.entity)
        self._equipment[equipment_slot] = None
        return equipment

    def _get_slots_of_type(self, equipment_type):
        return [e_slot for e_slot, e_type in
                EquipmentTypeAllowedInSlot.iteritems()
                if e_type == equipment_type]

    def _get_open_slots_of_type(self, equipment_type):
        return [slot for slot in self._get_slots_of_type(equipment_type)
                if self._equipment[slot] is None]

    def _all_slots_of_type_are_used(self, equipment_type):
        return len(self._get_open_slots_of_type(equipment_type)) < 1

    def can_equip(self, equipment):
        if(self._all_slots_of_type_are_used(equipment.equipment_type)):
            return False
        return True

    def try_equip(self, equipment):
        if self.can_equip(equipment):
            self._equip(equipment)
            return True
        return False

    def _equip(self, equipment):
        open_slots = self._get_open_slots_of_type(equipment.equipment_type)
        self._equip_into_slot(equipment, open_slots[0])

    def _equip_into_slot(self, equipment, slot):
        self._equipment[slot] = equipment
        equipment.equip_effect(self.entity)

    def execute_equip_effects(self):
        for equipment_slot in EquipmentSlots.ALL:
            if(self.slot_is_equiped(equipment_slot)):
                self._equipment[equipment_slot].equiped_effect(self.entity)
