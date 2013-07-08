import random
import entityeffect


class Action(object):
    def __init__(self):
        self.name = "XXX_Action_name"

    def act(self, source_entity, target_entity):
        pass


class ItemAction(Action):
    def __init__(self, source_item):
        super(ItemAction, self).__init__()
        self.name = "XXX_Action_name"
        self.source_item = source_item

    def act(self, source_entity, target_entity):
        pass


class DrinkAction(ItemAction):
    def __init__(self, source_item):
        super(DrinkAction, self).__init__(source_item)
        self.name = "Drink"

    def act(self, source_entity, target_entity):
        self.drink(target_entity)
        self.remove()

    def drink(self):
        pass

    def remove(self):
        self.source_item.inventory.remove_item(self.source_item)


class HealingPotionDrink(DrinkAction):
    def __init__(self, source_item):
        super(HealingPotionDrink, self).__init__(source_item)
        self.min_health = 5
        self.max_health = 10

    def drink(self, target_entity):
        health = random.randrange(self.min_health, self.max_health)
        heal_effect = entityeffect.Heal(target_entity, target_entity, health)
        target_entity.add_entity_effect(heal_effect)
