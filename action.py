import random
import messenger
import gametime
import entityeffect

#  Arguments:
SOURCE_ENTITY = "source_entity"
TARGET_ENTITY = "target_entity"
GAME_STATE = "game_state"


class Action(object):
    def __init__(self):
        self.name = "XXX_Action_Name_XX"
        self.display_order = 100
        self.energy_cost = gametime.single_turn

    def act(self, **kwargs):
        pass

    def can_act(self, **kwargs):
        return True

    def add_energy_spent_to_entity(self, entity):
        entity.newly_spent_energy += self.energy_cost


class ItemAction(Action):
    def __init__(self, source_item):
        super(ItemAction, self).__init__()
        self.name = "XXX_Item_Action_Name_XXX"
        self.source_item = source_item

    def remove_from_inventory(self):
        self.source_item.inventory.remove_item(self.source_item)


class EquipAction(ItemAction):
    def __init__(self, source_item):
        super(EquipAction, self).__init__(source_item)
        self.name = "Equip"
        self.display_order = 90

    def act(self, **kwargs):
        target_entity = kwargs[TARGET_ENTITY]
        source_entity = kwargs[SOURCE_ENTITY]
        self.equip(target_entity)
        self.add_energy_spent_to_entity(source_entity)

    def can_act(self, **kwargs):
        target_entity = kwargs[TARGET_ENTITY]
        return target_entity.equipment.can_equip(self.source_item)

    def equip(self, target_entity):
        equip_effect = entityeffect.Equip(target_entity,
                                          target_entity, self.source_item)
        target_entity.add_entity_effect(equip_effect)
        self.remove_from_inventory()


class DrinkAction(ItemAction):
    def __init__(self, source_item):
        super(DrinkAction, self).__init__(source_item)
        self.name = "Drink"
        self.display_order = 90

    def act(self, **kwargs):
        target_entity = kwargs[TARGET_ENTITY]
        source_entity = kwargs[SOURCE_ENTITY]
        self.drink(target_entity)
        self.remove_from_inventory()
        self.add_energy_spent_to_entity(source_entity)

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
        source_entity = kwargs[SOURCE_ENTITY]
        if(not self.source_item.inventory is None):
            drop_successful =\
                self.source_item.inventory.try_drop_item(self.source_item)
            if(drop_successful):
                self.add_energy_spent_to_entity(source_entity)
        return


class DescendStairsAction(Action):
    def __init__(self):
        super(DescendStairsAction, self).__init__()
        self.name = "Descend Stairs"
        self.display_order = 50

    def act(self, **kwargs):
        target_entity = kwargs[TARGET_ENTITY]
        source_entity = kwargs[SOURCE_ENTITY]
        current_dungeon_level = target_entity.dungeon_level
        next_dungeon_level = current_dungeon_level.\
            dungeon.get_dungeon_level(current_dungeon_level.depth + 1)
        if(next_dungeon_level is None):
            return False
        destination_position = next_dungeon_level.up_stairs[0].position
        target_entity.try_move(destination_position, next_dungeon_level)
        self.add_energy_spent_to_entity(source_entity)


class PickUpItemAction(Action):
    def __init__(self):
        super(PickUpItemAction, self).__init__()
        self.name = "Pick Up"
        self.display_order = 70

    def can_act(self, **kwargs):
        source_entity = kwargs[SOURCE_ENTITY]
        item = self._get_item_on_floor(source_entity)
        print item
        return (not item is None and
                source_entity.inventory.has_room_for_item(item))

    def act(self, **kwargs):
        source_entity = kwargs[SOURCE_ENTITY]
        item = self._get_item_on_floor(source_entity)
        print "the item is: ", item
        pickup_succeded = source_entity.inventory.try_add(item)
        if(pickup_succeded):
            message = "Picked up: " + item.name
            messenger.messenger.message(message)
            source_entity.newly_spent_energy += gametime.single_turn

    def _get_item_on_floor(self, entity):
        return entity.dungeon_level.get_tile(entity.position).get_first_item()

    def print_player_error(self, **kwargs):
        source_entity = kwargs[SOURCE_ENTITY]
        item = self._get_item_on_floor(source_entity)
        if(item is None and
           not source_entity.inventory.has_room_for_item(item)):
            message = "Could not pick up: " + item.name +\
                ", the inventory is full."
            messenger.messenger.message(message)
