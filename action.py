import random
import entityeffect

#  Arguments:
SOURCE_ENTITY = "source_entity"
TARGET_ENTITY = "target_entity"


class Action(object):
    def __init__(self):
        self.name = "XXX_Action_name"
        self.display_order = 100

    def act(self, **kwargs):
        pass

    def can_act(self, **kwargs):
        return True


class ItemAction(Action):
    def __init__(self, source_item):
        super(ItemAction, self).__init__()
        self.name = "XXX_Action_name"
        self.source_item = source_item

    def remove(self):
        self.source_item.inventory.remove_item(self.source_item)


class EquipAction(ItemAction):
    def __init__(self, source_item):
        super(EquipAction, self).__init__(source_item)
        self.name = "Equip"
        self.display_order = 90

    def act(self, **kwargs):
        target_entity = kwargs[TARGET_ENTITY]
        self.equip(target_entity)

    def can_act(self, **kwargs):
        target_entity = kwargs[TARGET_ENTITY]
        return target_entity.equipment.can_equip(self.source_item)

    def equip(self, target_entity):
        equip_effect = entityeffect.Equip(target_entity,
                                          target_entity, self.source_item)
        target_entity.add_entity_effect(equip_effect)
        self.remove()


class DrinkAction(ItemAction):
    def __init__(self, source_item):
        super(DrinkAction, self).__init__(source_item)
        self.name = "Drink"
        self.display_order = 90

    def act(self, **kwargs):
        target_entity = kwargs[TARGET_ENTITY]
        self.drink(target_entity)
        self.remove()
        return True

    def drink(self):
        pass


class HealingPotionDrink(DrinkAction):
    def __init__(self, source_item):
        super(HealingPotionDrink, self).__init__(source_item)
        self.min_health = 5
        self.max_health = 10

    def drink(self, target_entity):
        health = random.randrange(self.min_health, self.max_health)
        heal_effect = entityeffect.Heal(target_entity, target_entity, health)
        target_entity.add_entity_effect(heal_effect)


class DropAction(ItemAction):
    def __init__(self, source_item):
        super(DropAction, self).__init__(source_item)
        self.name = "Drop"
        self.display_order = 110

    def act(self, **kwargs):
        if(not self.source_item.inventory is None):
            drop_successful =\
                self.source_item.inventory.try_drop_item(self.source_item)
            return drop_successful
        return False
