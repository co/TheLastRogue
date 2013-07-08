class EquipmentSlots(object):
    #  Armor
    HEADGEAR = 0
    ARMOR = 1
    GLOVES = 2
    BOOTS = 3

    #  Jewelry
    RIGHTRING = 4
    LEFTRING = 5
    AMULET = 6

    #  Weapons
    MAINHAND = 7
    OFFHAND = 8


class Equipment(object):
    def __init__(self):
        self._equipment = {
            EquipmentSlots.HEADGEAR: None,
            EquipmentSlots.ARMOR: None,
            EquipmentSlots.GLOVES: None,
            EquipmentSlots.BOOTS: None,

            EquipmentSlots.RIGHTRING: None,
            EquipmentSlots.LEFTRING: None,
            EquipmentSlots.AMULET: None,

            EquipmentSlots.MAINHAND: None,
            EquipmentSlots.OFFHAND: None
        }

    def has(self, equipment_slot):
        return not self._equipment[equipment_slot] is None

    def unequip(self, equipment_slot):
        equipment = self._equipment[equipment_slot]
        self._equipment[equipment_slot] = None
        return equipment

    def try_equip(self, equipment):
        if(self.has(equipment.equipment_slot)):
            return False
        self._equipment[equipment.equipment_slot] = equipment
        return True
